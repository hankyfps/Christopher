"""Grafische Oberfläche mit tkinter (Tabs: Übersicht, Laufwerke, Netzwerk, Bluetooth, Updates) im dunklen Neon-Stil.

Aufbau: Kopfzeile mit CPU/RAM/Festplatte/Netzwerk und den Knöpfen (auf jedem Tab sichtbar), darunter die
fünf Tabs, unten die Statuszeile. Optional ein Overlay (kleine Leiste ganz oben, siehe overlay.py).

Effizienz (Messwerte siehe README, Abschnitt Performance):
- Messung und langsame Abfragen laufen im Hintergrund-Thread (BackgroundRunner), auch das Lesen der Netzwerkzähler.
- Die Prozessliste (unter Windows der teuerste Teil) wird nur erstellt, wenn der Tab Übersicht sichtbar ist.
- Ist das Hauptfenster minimiert oder versteckt, wird nichts gezeichnet; Messung, Warnungen und CSV laufen weiter.
- Texte werden nur gesetzt, wenn sie sich ändern; die Meldungsliste ist auf MAX_ALERTS Einträge begrenzt.
"""
from __future__ import annotations

import logging
import queue
import sys
import time
import tkinter as tk
import tkinter.font as tkfont
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk

from .alerts import Level
from .bluetooth import BluetoothStatus, get_bluetooth_status
from .collector import Snapshot, format_uptime
from .config import Config
from .core import Monitor
from .drives import DriveInfo, DriveScanner
from .network import TrafficMeter, WlanStatus, format_bytes, format_rate, get_wlan_status
from .overlay import HotkeyListener, OverlayWindow
from .overlay_logic import POSITIONS, format_overlay_text, level_for
from .tasks import BackgroundRunner
from .updates import UpdateResult, list_updates, start_upgrade
from .winutil import IS_WINDOWS

log = logging.getLogger("monitor.gui")

METRICS = ("CPU", "RAM", "Festplatte")
MAX_ALERTS = 500
TAB_OVERVIEW, TAB_DRIVES, TAB_NETWORK, TAB_BT, TAB_UPDATES = range(5)

# Farbpalette aus der Cyberpunk-Version (v2.2 "Cyberpunk Code UI")
C = {
    "bg": "#05050b", "panel": "#090a16", "card": "#080a17", "track": "#11142a",
    "line": "#1c2140", "line2": "#262c52", "select": "#1a1f3d",
    "text": "#dbe6ff", "bright": "#f2f6ff", "muted": "#8f9bc4", "dim": "#4a5382",
    "cyan": "#00f0ff", "pink": "#ff2a6d", "yellow": "#f5e663", "green": "#39ff88",
}
RED, GREEN, BLUE, ORANGE, GREY = C["pink"], C["green"], C["cyan"], C["yellow"], C["muted"]
STATE_COLOR = {"normal": C["cyan"], "nah": C["yellow"], "alarm": C["pink"]}


def pick_font(candidates: tuple[str, ...], available: set[str]) -> str:
    for name in candidates:
        if name in available:
            return name
    return "TkDefaultFont"


class MonitorApp:
    def __init__(self, root: tk.Tk, monitor: Monitor, config_path: Path) -> None:
        self.root = root
        self.monitor = monitor
        self.config_path = config_path
        self.paused = False
        self._job: str | None = None

        self.runner = BackgroundRunner()
        self.scanner = DriveScanner()
        self.meter = TrafficMeter(history=60)
        self._last_run: dict[str, float] = {}          # Hintergrundaufgabe -> letzter Start
        self._external: set[str] | None = None         # bekannte externe Laufwerke
        self._nic_manual = bool(monitor.config.net_interface)
        self._wlan_names: list[str] = []
        self._nic_names: list[str] = []
        self._last_processes: tuple | None = None
        self._last_snap: Snapshot | None = None
        self._last_sample = None
        self._last_nic = ""
        self._last_drives: list[DriveInfo] | None = None
        self._updates_checked = False
        self._texts: dict[int, str] = {}               # zuletzt gesetzter Text je Label (nur bei Änderung setzen)
        self._bar_styles: dict[int, str] = {}
        self._alert_count = 0
        self.overlay: OverlayWindow | None = None
        self._hidden_for_overlay = False
        self._hotkey_events: queue.Queue[str] = queue.Queue()
        self.hotkeys = HotkeyListener(monitor.config.overlay_hotkey, self._hotkey_events)

        root.title("System-Monitor")
        root.geometry("880x680")
        root.minsize(720, 560)
        root.configure(bg=C["bg"])
        root.protocol("WM_DELETE_WINDOW", self.quit)

        fams = set(tkfont.families(root))
        disp = pick_font(("Bahnschrift SemiBold", "Bahnschrift", "Segoe UI Semibold", "Segoe UI", "DejaVu Sans"), fams)
        mono = pick_font(("JetBrains Mono", "Cascadia Mono", "Consolas", "DejaVu Sans Mono"), fams)
        self.f_head = (disp, 10, "bold")
        self.f_mono = (mono, 10)
        self.f_small = (mono, 9)
        self.f_big = (disp, 11, "bold")

        self._setup_styles()
        self._build_widgets()
        self._choose_initial_nic()
        root.bind("<Map>", self._on_restore)
        self._job = root.after(500, self._tick)
        root.after(100, self._poll_background)
        if monitor.config.check_updates_on_start:
            root.after(3000, self.check_updates)
        self._hotkey_ok = self.hotkeys.start()
        if monitor.config.overlay_enabled:
            root.after(800, self.toggle_overlay)

    # ================================================================== Hilfen
    def _set(self, widget, text: str, **kw) -> None:
        """Text nur setzen, wenn er sich geändert hat (spart Neuzeichnen)."""
        if self._texts.get(id(widget)) != text or kw:
            self._texts[id(widget)] = text
            widget.config(text=text, **kw)

    def _set_bar(self, bar: ttk.Progressbar, value: float, level: str) -> None:
        style = f"{level}.Horizontal.TProgressbar"
        if self._bar_styles.get(id(bar)) != style:
            self._bar_styles[id(bar)] = style
            bar.configure(style=style)
        if abs(float(bar["value"]) - value) >= 0.05:
            bar["value"] = value

    def _viewable(self) -> bool:
        """False bei minimiertem oder verstecktem Hauptfenster -> dann nichts zeichnen."""
        try:
            return bool(self.root.winfo_viewable())
        except tk.TclError:
            return False

    # ================================================================== Aufbau
    def _setup_styles(self) -> None:
        s = ttk.Style(self.root)
        s.theme_use("clam")       # 'clam' erlaubt farbige Fortschrittsbalken
        s.configure(".", background=C["card"], foreground=C["text"], font=self.f_mono, bordercolor=C["line2"],
                    lightcolor=C["card"], darkcolor=C["card"], troughcolor=C["track"])
        s.configure("TFrame", background=C["card"])
        s.configure("TLabel", background=C["card"], foreground=C["text"])
        s.configure("TLabelframe", background=C["card"], bordercolor=C["line2"])
        s.configure("TLabelframe.Label", background=C["card"], foreground=C["cyan"], font=self.f_head)
        s.configure("Head.TFrame", background=C["panel"])
        s.configure("Head.TLabel", background=C["panel"], foreground=C["text"])
        s.configure("Value.Head.TLabel", background=C["panel"], foreground=C["bright"], font=self.f_big)
        s.configure("TButton", background=C["track"], foreground=C["cyan"], bordercolor=C["cyan"],
                    lightcolor=C["track"], darkcolor=C["track"], padding=(10, 4), font=self.f_head)
        s.map("TButton", background=[("active", C["select"]), ("disabled", C["panel"])],
              foreground=[("disabled", C["dim"])])
        s.configure("TCheckbutton", background=C["card"], foreground=C["text"])
        s.map("TCheckbutton", background=[("active", C["card"])])
        s.configure("TNotebook", background=C["bg"], borderwidth=0, tabmargins=(0, 4, 0, 0))
        s.configure("TNotebook.Tab", background=C["panel"], foreground=C["muted"], padding=(14, 6), font=self.f_head,
                    bordercolor=C["line2"])
        s.map("TNotebook.Tab", background=[("selected", C["card"])], foreground=[("selected", C["cyan"])])
        for name, color in (("normal", C["cyan"]), ("nah", C["yellow"]), ("alarm", C["pink"])):
            s.configure(f"{name}.Horizontal.TProgressbar", background=color, lightcolor=color, darkcolor=color,
                        troughcolor=C["track"], bordercolor=C["line2"], thickness=14)
        s.configure("Treeview", background=C["card"], fieldbackground=C["card"], foreground=C["text"],
                    rowheight=22, borderwidth=0, font=self.f_mono)
        s.map("Treeview", background=[("selected", C["select"])], foreground=[("selected", C["bright"])])
        s.configure("Treeview.Heading", background=C["track"], foreground=C["cyan"], font=self.f_head, relief="flat",
                    padding=(6, 4), borderwidth=0)
        s.map("Treeview.Heading", background=[("active", C["select"])])
        s.configure("Vertical.TScrollbar", troughcolor=C["card"], background=C["line2"], arrowcolor=C["muted"],
                    bordercolor=C["card"], gripcount=0)
        s.map("Vertical.TScrollbar", background=[("active", C["dim"])])
        for w in ("TSpinbox", "TEntry", "TCombobox"):
            s.configure(w, fieldbackground=C["track"], foreground=C["bright"], background=C["line2"],
                        arrowcolor=C["cyan"], insertcolor=C["cyan"], selectbackground=C["select"],
                        selectforeground=C["bright"], padding=3)
            s.map(w, bordercolor=[("focus", C["cyan"])], fieldbackground=[("readonly", C["track"])],
                  foreground=[("readonly", C["bright"])])
        # Aufklappliste der Combobox ist ein klassisches Listbox-Widget
        self.root.option_add("*TCombobox*Listbox.background", C["track"])
        self.root.option_add("*TCombobox*Listbox.foreground", C["bright"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", C["select"])
        self.root.option_add("*TCombobox*Listbox.font", self.f_mono)

    def _build_widgets(self) -> None:
        self._build_header().pack(fill="x")
        tk.Frame(self.root, bg=C["line"], height=1).pack(fill="x")
        bar = tk.Frame(self.root, bg=C["panel"])
        bar.pack(fill="x", side="bottom")
        self.hdr_net = tk.Label(bar, text="↓ –   ↑ –", bg=C["panel"], fg=C["cyan"], font=self.f_small, padx=8)
        self.hdr_net.pack(side="right")
        self.status = tk.Label(bar, text="Starte …", anchor="w", bg=C["panel"], fg=C["muted"],
                               font=self.f_small, padx=8, pady=3)
        self.status.pack(side="left", fill="x", expand=True)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=6, pady=(6, 4))
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        tabs = {}
        for key, title in (("overview", "Übersicht"), ("drives", "Laufwerke"), ("network", "Netzwerk / WLAN"),
                           ("bt", "Bluetooth"), ("updates", "Updates")):
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=title)
            tabs[key] = frame
        self._build_overview(tabs["overview"])
        self._build_drives(tabs["drives"])
        self._build_network(tabs["network"])
        self._build_bluetooth(tabs["bt"])
        self._build_updates(tabs["updates"])

    def _build_header(self) -> ttk.Frame:
        """Kennzahlen und Knöpfe – auf jedem Tab sichtbar. Zwei Zeilen, passt in 720 px Breite."""
        head = ttk.Frame(self.root, style="Head.TFrame")
        row1 = ttk.Frame(head, style="Head.TFrame")
        row1.pack(fill="x", padx=10, pady=(8, 2))
        self.bars: dict[str, ttk.Progressbar] = {}
        self.value_labels: dict[str, ttk.Label] = {}
        for col, name in enumerate(METRICS):
            ttk.Label(row1, text="Platte" if name == "Festplatte" else name, style="Head.TLabel",
                      width=6).grid(row=0, column=col * 3, sticky="w")
            bar = ttk.Progressbar(row1, maximum=100, length=110, style="normal.Horizontal.TProgressbar")
            bar.grid(row=0, column=col * 3 + 1, sticky="ew", padx=(0, 6))
            lbl = ttk.Label(row1, text="–", style="Value.Head.TLabel", width=7, anchor="e")
            lbl.grid(row=0, column=col * 3 + 2, sticky="e", padx=(0, 14))
            row1.columnconfigure(col * 3 + 1, weight=1)
            self.bars[name], self.value_labels[name] = bar, lbl
        row2 = ttk.Frame(head, style="Head.TFrame")
        row2.pack(fill="x", padx=10, pady=(2, 8))
        self.pause_btn = ttk.Button(row2, text="Pause", command=self.toggle_pause)
        self.pause_btn.pack(side="left")
        ttk.Button(row2, text="Einstellungen", command=self.open_settings).pack(side="left", padx=6)
        self.overlay_btn = ttk.Button(row2, text="Overlay", command=self.toggle_overlay)
        self.overlay_btn.pack(side="left")
        ttk.Button(row2, text="Beenden", command=self.quit).pack(side="right")
        return head

    @staticmethod
    def _wrap_to(parent, label: ttk.Label, margin: int = 24) -> None:
        """Zeilenumbruch des Labels an die Breite des Eltern-Widgets koppeln (kein Abschneiden bei 720 px)."""
        parent.bind("<Configure>", lambda e: label.config(wraplength=max(200, e.width - margin)), add="+")

    @staticmethod
    def _tree(parent, columns: list[tuple[str, str, int, str]], height: int = 8, selectmode="browse"):
        """Treeview mit Scrollbar. columns: (id, Überschrift, Breite, Ausrichtung)."""
        frame = ttk.Frame(parent)
        tree = ttk.Treeview(frame, columns=[c[0] for c in columns], show="headings",
                            height=height, selectmode=selectmode)
        for cid, head, width, anchor in columns:
            tree.heading(cid, text=head)
            tree.column(cid, width=width, anchor=anchor)
        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        return frame, tree

    # ------------------------------------------------------------ Tab Übersicht
    def _build_overview(self, tab: ttk.Frame) -> None:
        pad = {"padx": 8, "pady": 4}
        self.info_label = ttk.Label(tab, text="", foreground=C["muted"], wraplength=680, justify="left")
        self.info_label.pack(fill="x", **pad)
        self._wrap_to(tab, self.info_label)

        frm_p = ttk.LabelFrame(tab, text="Top-Prozesse (nach CPU)")
        frm_p.pack(fill="both", expand=True, **pad)
        box, self.tree = self._tree(frm_p, [("pid", "PID", 70, "e"), ("name", "Name", 280, "w"),
                                            ("cpu", "CPU %", 80, "e"), ("ram", "RAM %", 80, "e"),
                                            ("mb", "RAM MB", 90, "e")], height=7)
        box.pack(fill="both", expand=True, padx=4, pady=4)
        self.proc_hint = ttk.Label(frm_p, text="", foreground=C["muted"])
        self.proc_hint.pack(anchor="w", padx=6, pady=(0, 4))

        frm_a = ttk.LabelFrame(tab, text="Meldungen")
        frm_a.pack(fill="both", **pad)
        self.alert_list = tk.Listbox(frm_a, height=6, font=(self.f_small[0], 9), bg=C["card"], fg=C["text"],
                                     selectbackground=C["select"], selectforeground=C["bright"],
                                     highlightthickness=0, borderwidth=0)
        sb = ttk.Scrollbar(frm_a, orient="vertical", command=self.alert_list.yview)
        self.alert_list.configure(yscrollcommand=sb.set)
        self.alert_list.pack(side="left", fill="both", expand=True, padx=(4, 0), pady=4)
        sb.pack(side="right", fill="y", pady=4)
        ttk.Button(tab, text="Meldungen leeren", command=self._clear_alerts).pack(anchor="e", padx=8, pady=(0, 4))

    # ------------------------------------------------------------ Tab Laufwerke
    def _build_drives(self, tab: ttk.Frame) -> None:
        top = ttk.Frame(tab)
        top.pack(fill="x", padx=8, pady=6)
        self.drive_summary = ttk.Label(top, text="Lese Laufwerke …")
        self.drive_summary.pack(side="left")
        ttk.Button(top, text="Aktualisieren", command=lambda: self._refresh("drives", force=True)).pack(side="right")
        box, self.drive_tree = self._tree(tab, [
            ("mp", "Laufwerk", 110, "w"), ("kind", "Typ", 150, "w"), ("fs", "Dateisystem", 90, "w"),
            ("used", "Belegt", 90, "e"), ("free", "Frei", 90, "e"), ("total", "Gesamt", 90, "e"),
            ("pct", "Belegung", 80, "e")], height=12)
        box.pack(fill="both", expand=True, padx=8, pady=4)
        self.drive_tree.tag_configure("extern", foreground=BLUE)
        self.drive_tree.tag_configure("voll", foreground=RED)
        ttk.Label(tab, foreground=GREY, text="Blau = externes Speichermedium (USB, SD-Karte). "
                  "Rot = Belegung über der Festplatten-Schwelle.").pack(anchor="w", padx=8, pady=(0, 6))

    # ------------------------------------------------------------ Tab Netzwerk
    def _build_network(self, tab: ttk.Frame) -> None:
        pad = {"padx": 8, "pady": 3}
        frm_w = ttk.LabelFrame(tab, text="WLAN-Verbindung")
        frm_w.pack(fill="x", padx=8, pady=6)
        frm_w.columnconfigure(1, weight=1)
        self.wlan_labels: dict[str, ttk.Label] = {}
        rows = (("adapter", "Adapter"), ("state", "Status"), ("ssid", "Netzwerk (SSID)"),
                ("radio", "Standard / Band / Kanal"), ("rate", "Empfangs-/Senderate"), ("auth", "Sicherheit"))
        for r, (key, text) in enumerate(rows):
            ttk.Label(frm_w, text=text + ":").grid(row=r, column=0, sticky="w", **pad)
            lbl = ttk.Label(frm_w, text="–")
            lbl.grid(row=r, column=1, columnspan=2, sticky="w", **pad)
            self.wlan_labels[key] = lbl
        r = len(rows)
        ttk.Label(frm_w, text="Signal:").grid(row=r, column=0, sticky="w", **pad)
        sig_frame = ttk.Frame(frm_w)
        sig_frame.grid(row=r, column=1, columnspan=2, sticky="w", **pad)
        self.signal_bar = ttk.Progressbar(sig_frame, maximum=100, length=220, style="normal.Horizontal.TProgressbar")
        self.signal_bar.pack(side="left")
        self.signal_label = ttk.Label(sig_frame, text="–")
        self.signal_label.pack(side="left", padx=8)
        self.wlan_hint = ttk.Label(frm_w, text="", foreground=ORANGE, wraplength=640, justify="left")
        self._wrap_to(frm_w, self.wlan_hint, 40)
        self.wlan_hint.grid(row=r + 1, column=0, columnspan=3, sticky="w", **pad)
        ttk.Button(frm_w, text="Aktualisieren",
                   command=lambda: self._refresh("wlan", force=True)).grid(row=0, column=3, sticky="e", **pad)

        frm_t = ttk.LabelFrame(tab, text="Datenverkehr (Up & Down)")
        frm_t.pack(fill="both", expand=True, padx=8, pady=6)
        top = ttk.Frame(frm_t)
        top.pack(fill="x", padx=6, pady=4)
        ttk.Label(top, text="Netzwerkkarte:").pack(side="left")
        self.nic_var = tk.StringVar()
        self.nic_box = ttk.Combobox(top, textvariable=self.nic_var, state="readonly", width=30)
        self.nic_box.pack(side="left", padx=6)
        self.nic_box.bind("<<ComboboxSelected>>", self._on_nic_selected)
        self.down_label = ttk.Label(top, text="↓ –", foreground=BLUE, font=self.f_big)
        self.down_label.pack(side="left", padx=(20, 10))
        self.up_label = ttk.Label(top, text="↑ –", foreground=C["pink"], font=self.f_big)
        self.up_label.pack(side="left")
        self.total_label = ttk.Label(frm_t, text="", foreground=GREY)
        self.total_label.pack(anchor="w", padx=6)
        self.graph = tk.Canvas(frm_t, height=170, background=C["card"], highlightthickness=1,
                               highlightbackground=C["line2"])
        self.graph.pack(fill="both", expand=True, padx=6, pady=6)
        # neu zeichnen, sobald die Größe bekannt ist bzw. sich ändert (z. B. beim Wechsel auf den Tab)
        self.graph.bind("<Configure>", lambda _e: self._draw_graph())

    # ------------------------------------------------------------ Tab Bluetooth
    def _build_bluetooth(self, tab: ttk.Frame) -> None:
        top = ttk.Frame(tab)
        top.pack(fill="x", padx=8, pady=6)
        self.bt_adapter = ttk.Label(top, text="Lese Bluetooth …")
        self.bt_adapter.pack(side="left")
        ttk.Button(top, text="Aktualisieren", command=lambda: self._refresh("bt", force=True)).pack(side="right")
        box, self.bt_tree = self._tree(tab, [("name", "Gerät", 330, "w"), ("kind", "Typ", 80, "w"),
                                             ("conn", "Verbindung", 130, "w"), ("pnp", "Gerätestatus", 110, "w")],
                                       height=12)
        box.pack(fill="both", expand=True, padx=8, pady=4)
        self.bt_tree.tag_configure("on", foreground=GREEN)
        self.bt_tree.tag_configure("off", foreground=GREY)
        self.bt_hint = ttk.Label(tab, foreground=GREY, wraplength=680, justify="left", text=(
            "Gezeigt werden gekoppelte Geräte. Der Verbindungsstatus stammt aus einer nicht dokumentierten "
            "Windows-Geräteeigenschaft und kann bei manchen Geräten abweichen. Die Abfrage dauert einige Sekunden."))
        self.bt_hint.pack(anchor="w", padx=8, pady=(0, 6))
        self._wrap_to(tab, self.bt_hint)

    # ------------------------------------------------------------ Tab Updates
    def _build_updates(self, tab: ttk.Frame) -> None:
        top = ttk.Frame(tab)
        top.pack(fill="x", padx=8, pady=6)
        self.upd_status = ttk.Label(top, text="Noch nicht gesucht.")
        self.upd_status.pack(side="left")
        ttk.Button(top, text="Alle aktualisieren", command=lambda: self.install_updates(all_=True)).pack(side="right")
        ttk.Button(top, text="Ausgewählte aktualisieren", command=self.install_updates).pack(side="right", padx=6)
        self.upd_btn = ttk.Button(top, text="Nach Updates suchen", command=self.check_updates)
        self.upd_btn.pack(side="right")
        box, self.upd_tree = self._tree(tab, [
            ("name", "Name", 260, "w"), ("id", "ID", 210, "w"), ("inst", "Installiert", 110, "w"),
            ("avail", "Verfügbar", 110, "w"), ("src", "Quelle", 70, "w")], height=14, selectmode="extended")
        box.pack(fill="both", expand=True, padx=8, pady=4)
        upd_hint = ttk.Label(tab, foreground=GREY, wraplength=680, justify="left", text=(
            "Die Aktualisierung läuft in einem eigenen Konsolenfenster über winget. Manche Programme fragen dabei "
            "per Benutzerkontensteuerung nach Administratorrechten."))
        upd_hint.pack(anchor="w", padx=8, pady=(0, 6))
        self._wrap_to(tab, upd_hint)

    # ================================================================== Ablauf
    def _processes_wanted(self) -> bool:
        """Prozessliste nur, wenn man sie sieht: Fenster sichtbar und Tab Übersicht offen."""
        return self._viewable() and self._current_tab() == TAB_OVERVIEW

    def _measure(self, skip_processes: bool):
        """Läuft im Hintergrund-Thread: Messung und Netzwerkzähler lesen (psutil, ~6 ms)."""
        return self.monitor.step(skip_processes=skip_processes), self.meter.read()

    def _tick(self) -> None:
        """Wird alle interval_s Sekunden über root.after() aufgerufen.
        Die eigentliche Messung läuft im Hintergrund-Thread, damit das Fenster nie einfriert.
        Ist die vorige Messung noch nicht fertig, wird diese Runde übersprungen."""
        try:
            skip = not self._processes_wanted()
            self.runner.submit("measure", lambda: self._measure(skip),
                               lambda res: self._handle("Messung", res, self._show_measurement))
            self._refresh("drives")                      # psutil, schnell -> immer (für USB-Meldungen)
            if self._viewable():
                tab = self._current_tab()
                if tab == TAB_NETWORK:
                    self._refresh("wlan")                # netsh nur bei geöffnetem Tab
                elif tab == TAB_BT:
                    self._refresh("bt")                  # PowerShell nur bei geöffnetem Tab
        except Exception as exc:
            log.exception("Fehler im Zyklus")
            self.status.config(text=f"Fehler: {exc}")
        self._job = self.root.after(int(self.monitor.config.interval_s * 1000), self._tick)

    def _show_measurement(self, result) -> None:
        (snap, alerts), counters = result
        self._last_snap = snap
        for a in alerts:
            self._add_message(a.message(), RED if a.level is Level.WARNUNG else GREEN,
                              bell=a.level is Level.WARNUNG)
        self._update_traffic(counters)                   # Rate wird immer berechnet (Overlay braucht sie)
        if self._viewable():
            self._show_snapshot(snap)
            self.status.config(text=f"Letzte Messung: {snap.timestamp:%H:%M:%S}   "
                                    f"Intervall: {self.monitor.config.interval_s:g} s   "
                                    f"Messdauer: {self.monitor.last_duration_s * 1000:.0f} ms")
        self._update_overlay()

    def _current_tab(self) -> int:
        try:
            return self.notebook.index("current")
        except tk.TclError:
            return TAB_OVERVIEW

    def _on_tab_changed(self, _event=None) -> None:
        tab = self._current_tab()
        if tab == TAB_NETWORK:
            self._refresh("wlan")
            self._draw_graph()
        elif tab == TAB_BT:
            self._refresh("bt")
        elif tab == TAB_UPDATES and not self._updates_checked:
            self.check_updates()

    def _on_restore(self, event=None) -> None:
        """Hauptfenster wieder sichtbar (aus Minimierung oder Versteck): einmal alles auffrischen."""
        if event is not None and event.widget is not self.root:
            return
        if self._last_snap is not None:
            self._show_snapshot(self._last_snap)
        if self._last_drives is not None:
            self._show_drives(self._last_drives)
        self._show_traffic_labels()
        self._draw_graph()

    def _poll_background(self) -> None:
        self.runner.poll()
        try:
            while True:
                if self._hotkey_events.get_nowait() == "toggle":
                    self.toggle_overlay()
        except queue.Empty:
            pass
        self.root.after(100, self._poll_background)

    def _refresh(self, key: str, force: bool = False) -> None:
        """Startet eine Hintergrundabfrage, wenn ihr Intervall abgelaufen ist (oder force)."""
        cfg = self.monitor.config
        interval = {"drives": cfg.drive_refresh_s, "wlan": cfg.wlan_refresh_s, "bt": cfg.bt_refresh_s}[key]
        now = time.monotonic()
        if not force and now - self._last_run.get(key, -1e9) < interval:
            return
        jobs = {"drives": (self.scanner.scan, self._show_drives),
                "wlan": (get_wlan_status, self._show_wlan),
                "bt": (get_bluetooth_status, self._show_bluetooth)}
        func, callback = jobs[key]
        if self.runner.submit(key, func, lambda res, cb=callback, k=key: self._handle(k, res, cb)):
            self._last_run[key] = now

    def _handle(self, key: str, result, callback) -> None:
        if isinstance(result, Exception):
            self.status.config(text=f"{key}: Fehler – {result}")
            return
        callback(result)

    def _add_message(self, text: str, color: str, bell: bool = False) -> None:
        lb = self.alert_list
        lb.insert("end", text)
        lb.itemconfig("end", foreground=color)
        self._alert_count += 1
        if lb.size() > MAX_ALERTS:                       # Obergrenze: älteste Einträge entfernen
            lb.delete(0, lb.size() - MAX_ALERTS - 1)
        lb.see("end")
        if bell:
            self.root.bell()

    def _clear_alerts(self) -> None:
        self.alert_list.delete(0, "end")

    # ------------------------------------------------------------ Anzeige Übersicht
    def _show_snapshot(self, s: Snapshot) -> None:
        thresholds = self.monitor.config.thresholds()
        pcts = {"CPU": s.cpu_percent, "RAM": s.ram_percent, "Festplatte": s.disk_percent}
        for name, pct in pcts.items():
            self._set_bar(self.bars[name], pct, level_for(pct, thresholds[name]))
            self._set(self.value_labels[name], f"{pct:.1f} %")
        self._set(self.info_label,
                  f"CPU {s.cpu_cores} Kerne  |  RAM {s.ram_used_gb:.1f} / {s.ram_total_gb:.1f} GB  |  "
                  f"{s.disk_path} {s.disk_used_gb:.0f} / {s.disk_total_gb:.0f} GB  |  "
                  f"Laufzeit {format_uptime(s.uptime_s)}  |  Schwellen: "
                  + ", ".join(f"{k} {v:.0f} %" for k, v in thresholds.items()))
        if not self._processes_wanted():
            return
        if s.processes is not self._last_processes:     # Prozessliste unverändert -> Tabelle nicht neu aufbauen
            self._last_processes = s.processes
            self.tree.delete(*self.tree.get_children())
            for p in s.processes:
                self.tree.insert("", "end", values=(p.pid, p.name, f"{p.cpu_percent:.1f}",
                                                    f"{p.memory_percent:.1f}", f"{p.memory_mb:.0f}"))
        self._set(self.proc_hint, "" if s.processes else "Prozessliste wird erstellt …")

    # ------------------------------------------------------------ Anzeige Laufwerke
    def _show_drives(self, drives: list[DriveInfo]) -> None:
        self._last_drives = drives
        external = {d.mountpoint for d in drives if d.external}
        if self._viewable():
            limit = self.monitor.config.disk_threshold
            self.drive_tree.delete(*self.drive_tree.get_children())
            for d in drives:
                tags = ("voll",) if d.percent >= limit else ("extern",) if d.external else ()
                self.drive_tree.insert("", "end", tags=tags, values=(
                    d.mountpoint, d.kind, d.fstype, f"{d.used_gb:.1f} GB", f"{d.free_gb:.1f} GB",
                    f"{d.total_gb:.1f} GB", f"{d.percent:.1f} %"))
            self.drive_summary.config(text=f"{len(drives)} Laufwerk(e), davon {len(external)} extern"
                                           f"   (Stand {datetime.now():%H:%M:%S})")
        if self._external is not None:                  # beim ersten Einlesen nicht melden
            zeit = datetime.now().strftime("%H:%M:%S")
            for mp in sorted(external - self._external):
                self._add_message(f"{zeit}  INFO     Externes Laufwerk angeschlossen: {mp}", BLUE)
                log.info("Externes Laufwerk angeschlossen: %s", mp)
            for mp in sorted(self._external - external):
                self._add_message(f"{zeit}  INFO     Externes Laufwerk entfernt: {mp}", BLUE)
                log.info("Externes Laufwerk entfernt: %s", mp)
        self._external = external

    # ------------------------------------------------------------ Anzeige WLAN / Traffic
    def _show_wlan(self, status: WlanStatus) -> None:
        self.wlan_hint.config(text=status.message)
        info = next((i for i in status.interfaces if i.connected), status.interfaces[0] if status.interfaces else None)
        if info is None:
            for lbl in self.wlan_labels.values():
                lbl.config(text="–")
            self.signal_bar["value"] = 0
            self.signal_label.config(text="–")
            return
        band = " / ".join(x for x in (info.radio, info.band, f"Kanal {info.channel}" if info.channel else "") if x)
        rate = " / ".join(x for x in (info.rx_mbit, info.tx_mbit) if x)
        self.wlan_labels["adapter"].config(text=f"{info.name}  ({info.description})" if info.description else info.name)
        self.wlan_labels["state"].config(text=info.state or "–", foreground=GREEN if info.connected else RED)
        self.wlan_labels["ssid"].config(text=info.ssid or "– (nicht lesbar)")
        self.wlan_labels["radio"].config(text=band or "–")
        # netsh liefert reine Zahlen (MBit/s), Get-NetAdapter Text wie "866.7 Mbps"
        has_unit = any(ch.isalpha() for ch in rate)
        self.wlan_labels["rate"].config(text=(rate if has_unit else f"{rate} MBit/s") if rate else "–")
        self.wlan_labels["auth"].config(text=info.auth or "–")
        sig = info.signal or 0
        self.signal_bar["value"] = sig
        self.signal_bar.configure(style=("normal" if sig >= 60 else "nah" if sig >= 30 else "alarm")
                                  + ".Horizontal.TProgressbar")
        self.signal_label.config(text=f"{info.signal} %" if info.signal is not None else "–")
        # WLAN-Adapter für die Traffic-Anzeige übernehmen (solange nicht manuell gewählt)
        self._wlan_names = [i.name for i in status.interfaces]
        if not self._nic_manual:
            nic = self.meter.guess_wlan(self._wlan_names)
            if nic and nic != self.nic_var.get():
                self.nic_var.set(nic)

    def _choose_initial_nic(self) -> None:
        names = self.meter.interfaces()
        self._nic_names = names
        self.nic_box["values"] = names
        cfg_nic = self.monitor.config.net_interface
        nic = cfg_nic if cfg_nic in names else (self.meter.guess_wlan() or self.meter.busiest())
        if nic:
            self.nic_var.set(nic)

    def _on_nic_selected(self, _event=None) -> None:
        self._nic_manual = True
        self._update_traffic(self.meter.read())

    def _update_traffic(self, counters: dict) -> None:
        """Rate berechnen (immer) und anzeigen (nur wenn das Fenster sichtbar ist)."""
        names = self.meter.interfaces(counters)
        if names != self._nic_names:                     # Auswahlliste nur bei Änderung neu setzen
            self._nic_names = names
            self.nic_box["values"] = names
        nic = self.nic_var.get()
        self._last_sample = self.meter.sample(nic, counters) if nic else None
        self._last_nic = nic
        if self._viewable():
            self._show_traffic_labels()
            if self._current_tab() == TAB_NETWORK:       # Diagramm nur zeichnen, wenn sichtbar
                self._draw_graph()

    def _show_traffic_labels(self) -> None:
        sample, nic = self._last_sample, self._last_nic
        if sample is None:
            self._set(self.down_label, "↓ –")
            self._set(self.up_label, "↑ –")
            self._set(self.hdr_net, "↓ –   ↑ –")
            self._set(self.total_label, "Keine Netzwerkkarte gewählt." if not nic else f"'{nic}' nicht gefunden.")
            return
        self._set(self.down_label, f"↓ {format_rate(sample.down_bps)}")
        self._set(self.up_label, f"↑ {format_rate(sample.up_bps)}")
        self._set(self.hdr_net, f"↓ {format_rate(sample.down_bps)}   ↑ {format_rate(sample.up_bps)}")
        self._set(self.total_label, f"Seit Programmstart: ↓ {format_bytes(sample.total_down)}   "
                                    f"↑ {format_bytes(sample.total_up)}")

    def _draw_graph(self) -> None:
        c = self.graph
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 150 or h < 80:            # Tab nicht sichtbar -> Größe noch unbekannt
            return
        left, top, bottom = 70, 10, 20
        data = list(self.meter.history)
        peak = max([max(d, u) for d, u in data] + [1024.0])
        for i in range(5):                                    # Gitterlinien mit Beschriftung
            y = top + (h - top - bottom) * i / 4
            c.create_line(left, y, w - 5, y, fill=C["line"])
            c.create_text(left - 5, y, text=format_rate(peak * (4 - i) / 4), anchor="e",
                          fill=GREY, font=(self.f_small[0], 8))
        c.create_text(left, h - 5, text=f"letzte {len(data)} Messungen", anchor="sw", fill=GREY,
                      font=(self.f_small[0], 8))
        c.create_text(w - 5, h - 5, text="↓ Download   ↑ Upload", anchor="se", fill=GREY,
                      font=(self.f_small[0], 8))
        if len(data) < 2:
            return
        step = (w - 5 - left) / (self.meter.history.maxlen - 1)
        x0 = w - 5 - step * (len(data) - 1)
        for idx, color in ((0, BLUE), (1, C["pink"])):
            pts = []
            for k, values in enumerate(data):
                pts += [x0 + k * step, top + (h - top - bottom) * (1 - values[idx] / peak)]
            c.create_line(*pts, fill=color, width=2)

    # ------------------------------------------------------------ Anzeige Bluetooth
    def _show_bluetooth(self, status: BluetoothStatus) -> None:
        if status.adapters:
            text = "Adapter: " + ", ".join(f"{n} ({s})" for n, s in status.adapters)
        else:
            text = status.message or "Kein Bluetooth-Adapter gefunden."
        connected = sum(1 for d in status.devices if d.connected)
        if status.devices:
            text += f"   |   {len(status.devices)} gekoppelt, {connected} verbunden"
        self.bt_adapter.config(text=text)
        self.bt_tree.delete(*self.bt_tree.get_children())
        for d in status.devices:
            self.bt_tree.insert("", "end", tags=("on" if d.connected else "off",),
                                values=(d.name, d.kind, d.connection_text, d.status))

    # ------------------------------------------------------------ Updates
    def check_updates(self) -> None:
        self._updates_checked = True
        if self.runner.submit("updates", list_updates, lambda r: self._handle("updates", r, self._show_updates)):
            self.upd_status.config(text="Suche Updates mit winget … (kann bis zu einer Minute dauern)")
            self.upd_btn.state(["disabled"])

    def _show_updates(self, result: UpdateResult) -> None:
        self.upd_btn.state(["!disabled"])
        self.upd_tree.delete(*self.upd_tree.get_children())
        for u in result.updates:
            self.upd_tree.insert("", "end", iid=u.package_id,
                                 values=(u.name, u.package_id, u.installed, u.available, u.source))
        self.upd_status.config(text=f"{result.message}   (Stand {datetime.now():%H:%M})")
        tab_text = f"Updates ({len(result.updates)})" if result.updates else "Updates"
        self.notebook.tab(4, text=tab_text)

    def install_updates(self, all_: bool = False) -> None:
        if not IS_WINDOWS:
            messagebox.showinfo("Updates", "winget gibt es nur unter Windows.", parent=self.root)
            return
        ids = None if all_ else list(self.upd_tree.selection())
        if ids is not None and not ids:
            messagebox.showinfo("Updates", "Bitte zuerst ein oder mehrere Programme in der Liste markieren.",
                                parent=self.root)
            return
        what = "ALLE verfügbaren Updates" if ids is None else "\n".join(ids)
        if not messagebox.askyesno("Updates installieren",
                                   f"Folgendes wird mit winget aktualisiert:\n\n{what}\n\n"
                                   "Die betroffenen Programme sollten geschlossen sein. Einige Installer "
                                   "fragen nach Administratorrechten. Fortfahren?", parent=self.root):
            return
        try:
            start_upgrade(ids)
            self.upd_status.config(text="Aktualisierung im Konsolenfenster gestartet – danach erneut suchen.")
        except Exception as exc:
            messagebox.showerror("Updates", str(exc), parent=self.root)

    # ------------------------------------------------------------ Overlay
    def toggle_overlay(self) -> None:
        """Overlay ein-/ausschalten (Knopf oder Tastenkürzel). Das Hauptfenster wird nur versteckt,
        wenn das Tastenkürzel funktioniert – sonst käme man nicht mehr zurück."""
        cfg = self.monitor.config
        if self.overlay is None:
            fam = self.f_mono[0]
            self.overlay = OverlayWindow(self.root, cfg, (fam, 10, "bold"), C)
        ov = self.overlay
        if ov.visible:
            ov.hide()
            self.overlay_btn.config(text="Overlay")
            if self._hidden_for_overlay:
                self._hidden_for_overlay = False
                self.root.deiconify()
            return
        ov.apply_config(cfg)
        ov.show()
        self.overlay_btn.config(text="Overlay aus")
        self._update_overlay()
        if cfg.overlay_hide_main:
            if self._hotkey_ok:
                self._hidden_for_overlay = True
                self.root.withdraw()
            else:
                self.status.config(text="Overlay an – Hauptfenster bleibt sichtbar, "
                                        f"weil das Tastenkürzel {cfg.overlay_hotkey} nicht verfügbar ist.")

    def _update_overlay(self) -> None:
        ov, snap = self.overlay, self._last_snap
        if ov is None or not ov.visible or snap is None:
            return
        cfg = self.monitor.config
        sample = self._last_sample
        text = format_overlay_text(snap.cpu_percent, snap.ram_percent, sample.down_bps if sample else 0.0,
                                   sample.up_bps if sample else 0.0, f"{snap.timestamp:%H:%M}")
        order = {"normal": 0, "nah": 1, "alarm": 2}
        level = max((level_for(snap.cpu_percent, cfg.cpu_threshold), level_for(snap.ram_percent, cfg.ram_threshold),
                     level_for(snap.disk_percent, cfg.disk_threshold)), key=order.get)
        ov.update(text, STATE_COLOR[level])

    # ================================================================== Aktionen
    def toggle_pause(self) -> None:
        if self.paused:
            self.paused = False
            self.pause_btn.config(text="Pause")
            self._tick()
        else:
            self.paused = True
            if self._job:
                self.root.after_cancel(self._job)
                self._job = None
            self.pause_btn.config(text="Fortsetzen")
            self.status.config(text="Pausiert")

    def open_settings(self) -> None:
        SettingsDialog(self.root, self.monitor.config, self._apply_settings, self.f_mono)

    def _apply_settings(self, new_cfg: Config) -> None:
        old_hotkey = self.monitor.config.overlay_hotkey
        new_cfg.save(self.config_path)
        self.monitor.apply_config(new_cfg)
        if self.overlay is not None:
            self.overlay.apply_config(new_cfg)
        log.info("Einstellungen geändert: %s", new_cfg)
        note = "   (neues Tastenkürzel gilt nach Neustart)" if new_cfg.overlay_hotkey != old_hotkey else ""
        self.status.config(text="Einstellungen gespeichert" + note)

    def quit(self) -> None:
        if self._job:
            self.root.after_cancel(self._job)
        self.hotkeys.stop()
        if self.overlay is not None:
            self.overlay.destroy()
        self.monitor.close()                             # gepufferte CSV-Zeilen schreiben
        self.root.destroy()


class SettingsDialog(tk.Toplevel):
    FIELDS = (
        ("cpu_threshold", "CPU-Schwelle (%)", 1, 100, 1),
        ("ram_threshold", "RAM-Schwelle (%)", 1, 100, 1),
        ("disk_threshold", "Festplatten-Schwelle (%)", 1, 100, 1),
        ("hysteresis", "Hysterese (%-Punkte)", 0, 49, 1),
        ("interval_s", "Messintervall (s)", 0.5, 3600, 0.5),
        ("alert_cooldown_s", "Warnungs-Pause (s)", 0, 86400, 10),
        ("top_processes", "Anzahl Prozesse", 1, 50, 1),
        ("process_interval_s", "Prozessliste aktualisieren (s)", 1, 3600, 1),
        ("drive_refresh_s", "Laufwerke aktualisieren (s)", 2, 3600, 5),
        ("wlan_refresh_s", "WLAN aktualisieren (s)", 2, 3600, 5),
        ("bt_refresh_s", "Bluetooth aktualisieren (s)", 2, 3600, 5),
        ("overlay_alpha", "Overlay-Deckkraft (0,2 – 1)", 0.2, 1.0, 0.05),
    )
    INT_FIELDS = {"alert_cooldown_s", "top_processes", "drive_refresh_s", "wlan_refresh_s", "bt_refresh_s"}

    def __init__(self, parent: tk.Tk, config: Config, on_save, font) -> None:
        super().__init__(parent)
        self.title("Einstellungen")
        self.configure(bg=C["card"])
        self.resizable(False, False)
        self.transient(parent)
        self.config_obj = config
        self.on_save = on_save
        self.vars: dict[str, tk.StringVar] = {}

        for row, (key, label, lo, hi, step) in enumerate(self.FIELDS):
            ttk.Label(self, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=2)
            var = tk.StringVar(value=str(getattr(config, key)))
            ttk.Spinbox(self, from_=lo, to=hi, increment=step, textvariable=var, width=10).grid(
                row=row, column=1, padx=10, pady=2)
            self.vars[key] = var

        row = len(self.FIELDS)
        ttk.Label(self, text="Laufwerk/Pfad (leer = System)").grid(row=row, column=0, sticky="w", padx=10, pady=2)
        self.disk_var = tk.StringVar(value=config.disk_path)
        ttk.Entry(self, textvariable=self.disk_var, width=12).grid(row=row, column=1, padx=10, pady=2)
        row += 1
        ttk.Label(self, text="Overlay-Position").grid(row=row, column=0, sticky="w", padx=10, pady=2)
        self.pos_var = tk.StringVar(value=config.overlay_position)
        ttk.Combobox(self, textvariable=self.pos_var, values=POSITIONS, state="readonly", width=12).grid(
            row=row, column=1, padx=10, pady=2)
        row += 1
        ttk.Label(self, text="Overlay-Tastenkürzel (nach Neustart)").grid(row=row, column=0, sticky="w", padx=10, pady=2)
        self.hotkey_var = tk.StringVar(value=config.overlay_hotkey)
        ttk.Entry(self, textvariable=self.hotkey_var, width=12).grid(row=row, column=1, padx=10, pady=2)
        self.bools: dict[str, tk.BooleanVar] = {}
        for key, text in (("check_updates_on_start", "Sofort beim Start nach Updates suchen (sonst beim Öffnen des Tabs)"),
                          ("overlay_enabled", "Overlay beim Start anzeigen"),
                          ("overlay_click_through", "Overlay: Mausklicks gehen hindurch"),
                          ("overlay_hide_main", "Overlay: Hauptfenster verstecken, solange es an ist")):
            row += 1
            self.bools[key] = tk.BooleanVar(value=bool(getattr(config, key)))
            ttk.Checkbutton(self, text=text, variable=self.bools[key]).grid(
                row=row, column=0, columnspan=2, sticky="w", padx=10, pady=2)

        btns = ttk.Frame(self)
        btns.grid(row=row + 1, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text="Speichern", command=self._save).pack(side="left", padx=5)
        ttk.Button(btns, text="Abbrechen", command=self.destroy).pack(side="left", padx=5)

        self.grab_set()   # Dialog ist modal

    def _save(self) -> None:
        try:
            changes: dict = {}
            for key, *_ in self.FIELDS:
                value = float(self.vars[key].get().replace(",", "."))
                changes[key] = int(value) if key in self.INT_FIELDS else value
            changes["disk_path"] = self.disk_var.get().strip()
            changes["overlay_position"] = self.pos_var.get()
            changes["overlay_hotkey"] = self.hotkey_var.get().strip()
            for key, var in self.bools.items():
                changes[key] = bool(var.get())
            new_cfg = replace(self.config_obj, **changes)
            new_cfg.validate()
            if new_cfg.disk_path:
                import psutil
                psutil.disk_usage(new_cfg.disk_path)   # prüft, ob der Pfad existiert
        except (ValueError, OSError) as exc:
            messagebox.showerror("Ungültige Eingabe", str(exc), parent=self)
            return
        self.on_save(new_cfg)
        self.destroy()


def run_gui(monitor: Monitor, config_path: Path) -> None:
    # Python wechselt standardmäßig nur alle 5 ms zwischen Threads (GIL). Während der Mess-Thread
    # rechnet, wartet das Fenster bei jedem Tk-Aufruf bis zu 5 ms -> spürbares Ruckeln.
    # 1 ms hält das Fenster flüssig; der Mess-Thread wird dadurch kaum langsamer.
    sys.setswitchinterval(0.001)
    root = tk.Tk()
    MonitorApp(root, monitor, config_path)
    root.mainloop()
