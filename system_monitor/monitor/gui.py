"""Grafische Oberfläche mit tkinter im Cyberpunk-Look ("cp2077").

Aufbau: Kopfzeile (Status), Seitenleiste (Bedienung, Schwellen, System), Mitte mit
fünf Ansichten (Übersicht, Laufwerke, Netzwerk, Bluetooth, Updates) als Neon-Reiter,
rechts Meldungen und Legende, unten Statuszeile.

Effizienz:
- Messung und langsame Abfragen laufen im Hintergrund-Thread (BackgroundRunner).
- Labels, Balken und Tabellenzeilen werden nur geändert, wenn sich ihr Inhalt ändert;
  Tabellenzeilen der Prozessliste werden wiederverwendet.
- Nur die sichtbare Ansicht wird gezeichnet; WLAN/Bluetooth werden nur bei offener Ansicht abgefragt.
- Ist das Fenster minimiert oder versteckt, entfallen Prozess-Scan und Zeichnen; Messung, Warnungen und CSV laufen weiter.
- Die Prozessliste (unter Windows der teuerste Teil, gemessen ~7 ms je Prozess) wird nur erstellt, wenn die
  Ansicht Übersicht sichtbar ist. Die Netzwerkzähler werden im Mess-Thread gelesen.
- Overlay (overlay.py): kleine, immer sichtbare Anzeige in drei Stilen, ein-/ausschaltbar per Knopf und Tastenkürzel.
- Die Meldungsliste ist auf MAX_ALERTS Einträge begrenzt.
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

from . import __version__
from .alerts import Level
from .bluetooth import BluetoothStatus, get_bluetooth_status
from .collector import Snapshot, format_uptime
from .config import Config
from .core import Monitor
from .drives import DriveInfo, DriveScanner
from .network import TrafficMeter, WlanStatus, format_bytes, format_rate, get_wlan_status
from .overlay import HotkeyListener, OverlayWindow
from .overlay_logic import OVERLAY_STYLES, POSITIONS, OverlayData, level_for
from .tasks import BackgroundRunner
from .updates import UpdateResult, list_updates, start_upgrade
from .winutil import IS_WINDOWS

log = logging.getLogger("monitor.gui")

METRICS = ("CPU", "RAM", "Festplatte")
MAX_ALERTS = 500
TAB_OVERVIEW, TAB_DRIVES, TAB_NETWORK, TAB_BT, TAB_UPDATES = range(5)
VIEW_TITLES = ("ÜBERSICHT", "LAUFWERKE", "NETZWERK", "BLUETOOTH", "UPDATES")

# Farbpalette aus dem Entwurf "Cyberpunk Code UI"
C = {
    "bg": "#05050b", "panel": "#090a16", "card": "#080a17", "track": "#11142a",
    "line": "#1c2140", "line2": "#262c52", "select": "#1a1f3d",
    "text": "#dbe6ff", "bright": "#f2f6ff", "muted": "#8f9bc4", "dim": "#4a5382",
    "cyan": "#00f0ff", "pink": "#ff2a6d", "yellow": "#f5e663", "green": "#39ff88",
}
STATE_COLOR = {"normal": C["cyan"], "nah": C["yellow"], "alarm": C["pink"]}


def blend(fg: str, bg: str, alpha: float) -> str:
    """Mischt zwei Hex-Farben (tkinter kennt keine Transparenz)."""
    f = [int(fg[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(bg[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(a * alpha + c * (1 - alpha)):02x}" for a, c in zip(f, b))


def pick_font(candidates: tuple[str, ...], available: set[str]) -> str:
    for name in candidates:
        if name in available:
            return name
    return "TkDefaultFont"


# ---------------------------------------------------------------------- Bausteine
class NeonButton(tk.Canvas):
    """Button mit abgeschrägten Ecken. Per Maus, Tab + Enter/Leertaste bedienbar."""
    CUT = 9

    def __init__(self, parent, text: str, command, color: str, font, bg: str,
                 height: int = 40, width: int = 180) -> None:
        super().__init__(parent, width=width, height=height, bg=bg, bd=0,
                         highlightthickness=0, takefocus=1, cursor="hand2")
        self.command, self.color, self.bg = command, color, bg
        self._hover = self._focus = self._active = False
        self._poly = self.create_polygon(0, 0, 0, 0, outline=color, width=1, fill=blend(color, bg, 0.07))
        self._text = self.create_text(0, 0, text=text, fill=color, font=font)
        self.bind("<Configure>", self._layout)
        self.bind("<Enter>", lambda e: self._state(hover=True))
        self.bind("<Leave>", lambda e: self._state(hover=False))
        self.bind("<FocusIn>", lambda e: self._state(focus=True))
        self.bind("<FocusOut>", lambda e: self._state(focus=False))
        self.bind("<ButtonRelease-1>", self._click)
        self.bind("<Return>", lambda e: self.command())
        self.bind("<space>", lambda e: self.command())

    def _layout(self, e) -> None:
        w, h, c = e.width - 1, e.height - 1, self.CUT
        self.coords(self._poly, c, 0, w, 0, w, h - c, w - c, h, 0, h, 0, c)
        self.coords(self._text, e.width / 2, e.height / 2)

    def _state(self, hover: bool | None = None, focus: bool | None = None) -> None:
        if hover is not None:
            self._hover = hover
        if focus is not None:
            self._focus = focus
        alpha = 0.28 if self._active else 0.2 if (self._hover or self._focus) else 0.07
        self.itemconfig(self._poly, fill=blend(self.color, self.bg, alpha),
                        width=2 if (self._focus or self._active) else 1)

    def _click(self, e) -> None:
        if 0 <= e.x < self.winfo_width() and 0 <= e.y < self.winfo_height():
            self.command()

    def set(self, text: str | None = None, color: str | None = None, active: bool | None = None) -> None:
        if color:
            self.color = color
            self.itemconfig(self._poly, outline=color)
            self.itemconfig(self._text, fill=color)
        if active is not None:
            self._active = active
        if text is not None:
            self.itemconfig(self._text, text=text)
        self._state()

    def text(self) -> str:
        return self.itemcget(self._text, "text")


class NeonBar(tk.Canvas):
    """Balken mit Leuchtsaum und (optional) Markierung der Warnschwelle."""

    def __init__(self, parent, bg: str, height: int = 14) -> None:
        super().__init__(parent, height=height + 8, bg=bg, bd=0, highlightthickness=0)
        self.bg, self.h = bg, height
        self._pct, self._thr, self._color = 0.0, None, C["cyan"]
        self._track = self.create_rectangle(0, 0, 0, 0, fill=C["track"], outline=C["line2"])
        self._halo = self.create_rectangle(0, 0, 0, 0, fill=blend(self._color, bg, 0.22), outline="")
        self._fill = self.create_rectangle(0, 0, 0, 0, fill=self._color, outline="")
        self._mark = self.create_line(0, 0, 0, 0, fill=C["bright"], width=2)
        self.bind("<Configure>", lambda e: self._draw())

    @property
    def value(self) -> float:
        return self._pct

    def set(self, pct: float, threshold: float | None, color: str) -> None:
        if abs(pct - self._pct) < 0.05 and threshold == self._thr and color == self._color:
            return                                   # nichts geändert -> nicht zeichnen
        if color != self._color:
            self._color = color
            self.itemconfig(self._fill, fill=color)
            self.itemconfig(self._halo, fill=blend(color, self.bg, 0.22))
        self._pct, self._thr = pct, threshold
        self._draw()

    def _draw(self) -> None:
        w = self.winfo_width()
        if w <= 1:
            return
        top, h = 4, self.h
        x = max(0.0, min(100.0, self._pct)) / 100 * (w - 2)
        self.coords(self._track, 0, top, w - 1, top + h)
        self.coords(self._halo, 0, 0, x + 3 if x else 0, top + h + 4)
        self.coords(self._fill, 1, top + 1, x + 1 if x else 1, top + h)
        if self._thr is None:
            self.itemconfig(self._mark, state="hidden")
        else:
            tx = self._thr / 100 * (w - 2)
            self.itemconfig(self._mark, state="normal")
            self.coords(self._mark, tx, 0, tx, top + h + 4)


# ---------------------------------------------------------------------- Hauptfenster
class MonitorApp:
    def __init__(self, root: tk.Tk, monitor: Monitor, config_path: Path) -> None:
        self.root = root
        self.monitor = monitor
        self.config_path = config_path
        self.paused = False
        self._job: str | None = None
        self._texts: dict[int, str] = {}          # zuletzt gesetzter Text je Label
        self._rows: list[str] = []                 # Tabellenzeilen Prozessliste (iids)
        self._row_vals: list[tuple] = []
        self._alert_count = 0

        self.runner = BackgroundRunner()
        self.overlay: OverlayWindow | None = None
        self._hidden_for_overlay = False               # Hauptfenster wegen Overlay versteckt?
        self._hotkey_events: queue.Queue[str] = queue.Queue()
        self.hotkeys = HotkeyListener(monitor.config.overlay_hotkey, self._hotkey_events)
        self._last_sample = None                       # letzte Traffic-Rate (auch für das Overlay)
        self._last_nic = ""
        self.scanner = DriveScanner()
        self.meter = TrafficMeter(history=60)
        self._last_run: dict[str, float] = {}          # Hintergrundaufgabe -> letzter Start
        self._external: set[str] | None = None         # bekannte externe Laufwerke
        self._nic_manual = bool(monitor.config.net_interface)
        self._wlan_names: list[str] = []
        self._nic_names: list[str] = []
        self._last_processes: tuple | None = None
        self._updates_checked = False
        self._view = TAB_OVERVIEW

        root.title("SYSTEM//MONITOR")
        root.geometry("1220x760")
        root.minsize(1020, 640)
        root.configure(bg=C["bg"])
        root.protocol("WM_DELETE_WINDOW", self.quit)

        fams = set(tkfont.families(root))
        disp = pick_font(("Orbitron", "Bahnschrift SemiBold", "Bahnschrift", "Segoe UI Semibold",
                          "DejaVu Sans"), fams)
        mono = pick_font(("JetBrains Mono", "Cascadia Mono", "Consolas", "DejaVu Sans Mono"), fams)
        self.f_logo = (disp, 15, "bold")
        self.f_h = (disp, 10, "bold")
        self.f_btn = (disp, 9, "bold")
        self.f_big = (disp, 20, "bold")
        self.f_mono = (mono, 10)
        self.f_small = (mono, 9)

        self._setup_styles()
        self._build()
        self._choose_initial_nic()
        self.select_view(TAB_OVERVIEW)
        root.bind("<Map>", self._on_restore)
        self._job = root.after(500, self._tick)
        root.after(100, self._poll_background)
        if monitor.config.check_updates_on_start:
            root.after(3000, self.check_updates)
        self._hotkey_ok = self.hotkeys.start()
        if monitor.config.overlay_enabled:
            root.after(800, self.toggle_overlay)

    # ================================================================== Hilfen
    def _set(self, widget: tk.Widget, text: str, **kw) -> None:
        """Text nur setzen, wenn er sich geändert hat (spart Neuzeichnen)."""
        if self._texts.get(id(widget)) != text or kw:
            self._texts[id(widget)] = text
            widget.config(text=text, **kw)

    def _label(self, parent, text="", fg=None, font=None, bg=None, **kw) -> tk.Label:
        return tk.Label(parent, text=text, fg=fg or C["text"], bg=bg or parent["bg"],
                        font=font or self.f_mono, **kw)

    def _panel(self, parent, title: str, bg: str = C["card"]) -> tk.Frame:
        outer = tk.Frame(parent, bg=bg, highlightthickness=1, highlightbackground=C["line2"])
        head = tk.Frame(outer, bg=bg)
        head.pack(fill="x")
        self._label(head, f"// {title}", fg=C["cyan"], font=self.f_h).pack(side="left", padx=14, pady=(9, 8))
        outer.head = head
        tk.Frame(outer, bg=C["line"], height=1).pack(fill="x")
        body = tk.Frame(outer, bg=bg)
        body.pack(fill="both", expand=True)
        outer.body = body
        return outer

    def _hint(self, parent, text: str = "", fg: str | None = None) -> tk.Label:
        return self._label(parent, text, fg=fg or C["dim"], font=self.f_small, anchor="w",
                           justify="left", wraplength=560)

    def _small_button(self, parent, text: str, command, color: str = C["cyan"], width: int = 150):
        return NeonButton(parent, text, command, color, self.f_btn, parent["bg"], height=30, width=width)

    def _tree(self, parent, columns, height: int = 10, selectmode: str = "browse") -> ttk.Treeview:
        """Treeview im Neon-Stil mit Scrollbar. columns: (id, Überschrift, Breite, Ausrichtung, dehnbar)."""
        wrap = tk.Frame(parent, bg=C["card"])
        wrap.pack(fill="both", expand=True, padx=8, pady=8)
        tree = ttk.Treeview(wrap, columns=[c[0] for c in columns], show="headings", style="Neon.Treeview",
                            selectmode=selectmode, height=height)
        for cid, head, width, anchor, stretch in columns:
            tree.heading(cid, text=head, anchor=anchor)
            tree.column(cid, width=width, minwidth=50, anchor=anchor, stretch=stretch)
        tree.tag_configure("odd", background="#0b0d1c")
        sbar = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview, style="Neon.Vertical.TScrollbar")
        tree.configure(yscrollcommand=sbar.set)
        tree.pack(side="left", fill="both", expand=True)
        sbar.pack(side="right", fill="y")
        return tree

    def _setup_styles(self) -> None:
        s = ttk.Style(self.root)
        s.theme_use("clam")
        s.configure("Neon.Treeview", background=C["card"], fieldbackground=C["card"],
                    foreground=C["text"], rowheight=26, font=self.f_mono, borderwidth=0,
                    lightcolor=C["card"], darkcolor=C["card"], bordercolor=C["card"])
        s.map("Neon.Treeview", background=[("selected", C["select"])],
              foreground=[("selected", C["bright"])])
        s.configure("Neon.Treeview.Heading", background=C["track"], foreground=C["cyan"],
                    font=self.f_btn, relief="flat", borderwidth=0, padding=(8, 6),
                    lightcolor=C["track"], darkcolor=C["track"], bordercolor=C["line"])
        s.map("Neon.Treeview.Heading", background=[("active", C["select"])])
        s.layout("Neon.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        s.configure("Neon.Vertical.TScrollbar", troughcolor=C["card"], background=C["line2"],
                    arrowcolor=C["muted"], bordercolor=C["card"], lightcolor=C["line2"],
                    darkcolor=C["line2"], gripcount=0)
        s.map("Neon.Vertical.TScrollbar", background=[("active", C["dim"])])
        for w in ("TSpinbox", "TEntry", "TCombobox"):
            s.configure(f"Neon.{w}", fieldbackground=C["track"], foreground=C["bright"],
                        background=C["line2"], arrowcolor=C["cyan"], bordercolor=C["line2"],
                        lightcolor=C["track"], darkcolor=C["track"], insertcolor=C["cyan"],
                        selectbackground=C["select"], selectforeground=C["bright"], padding=4)
            s.map(f"Neon.{w}", bordercolor=[("focus", C["cyan"])],
                  fieldbackground=[("readonly", C["track"])], foreground=[("readonly", C["bright"])])
        # Aufklappliste der Combobox (ist ein klassisches Listbox-Widget)
        self.root.option_add("*TCombobox*Listbox.background", C["track"])
        self.root.option_add("*TCombobox*Listbox.foreground", C["bright"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", C["select"])
        self.root.option_add("*TCombobox*Listbox.font", self.f_mono)

    # ================================================================== Aufbau
    def _build(self) -> None:
        r = self.root
        r.columnconfigure(0, weight=1)
        r.rowconfigure(1, weight=1)
        self._build_header().grid(row=0, column=0, sticky="ew")
        tk.Frame(r, bg=C["line"], height=1).grid(row=0, column=0, sticky="sew")

        body = tk.Frame(r, bg=C["bg"])
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        self._build_sidebar(body).grid(row=0, column=0, sticky="ns")
        self._build_main(body).grid(row=0, column=1, sticky="nsew", padx=18, pady=18)
        self._build_right(body).grid(row=0, column=2, sticky="ns", pady=18, padx=(0, 18))

        bar = tk.Frame(r, bg=C["panel"], highlightthickness=1, highlightbackground=C["line"])
        bar.grid(row=2, column=0, sticky="ew")
        self.status = self._label(bar, "> starte …", fg=C["muted"], font=self.f_small, anchor="w")
        self.status.pack(side="left", padx=14, pady=5)
        self._label(bar, f"v{__version__}", fg=C["dim"], font=self.f_small).pack(side="right", padx=14)

    def _build_header(self) -> tk.Frame:
        h = tk.Frame(self.root, bg="#080914")
        logo = tk.Canvas(h, width=28, height=28, bg="#080914", highlightthickness=0)
        logo.create_polygon(14, 2, 25, 8, 25, 20, 14, 26, 3, 20, 3, 8, outline=C["cyan"], fill="", width=2)
        logo.create_line(9, 14, 19, 14, fill=C["pink"], width=2)
        logo.create_line(14, 9, 14, 19, fill=C["pink"], width=2)
        logo.pack(side="left", padx=(20, 10), pady=12)
        for txt, fg in (("SYSTEM", C["bright"]), ("//", C["pink"]), ("MONITOR", C["bright"])):
            self._label(h, txt, fg=fg, font=self.f_logo).pack(side="left")

        right = tk.Frame(h, bg="#080914")
        right.pack(side="right", padx=20)
        self.dot = tk.Canvas(right, width=10, height=10, bg="#080914", highlightthickness=0)
        self._dot = self.dot.create_oval(1, 1, 9, 9, fill=C["green"], outline="")
        self.dot.pack(side="left", padx=(0, 6))
        self.state_lbl = self._label(right, "LIVE", fg=C["green"], font=self.f_btn)
        self.state_lbl.pack(side="left", padx=(0, 18))
        self._label(right, "INTERVALL:", fg=C["muted"], font=self.f_btn).pack(side="left")
        self.interval_lbl = self._label(right, "", fg=C["cyan"], font=self.f_btn)
        self.interval_lbl.pack(side="left", padx=(4, 18))
        self._label(right, "LAUFZEIT:", fg=C["muted"], font=self.f_btn).pack(side="left")
        self.uptime_lbl = self._label(right, "–", fg=C["pink"], font=self.f_btn)
        self.uptime_lbl.pack(side="left", padx=(4, 0))
        return h

    def _build_sidebar(self, parent) -> tk.Frame:
        sb = tk.Frame(parent, bg=C["panel"], width=236, highlightthickness=1, highlightbackground=C["line"])
        sb.pack_propagate(False)
        bg = C["panel"]
        self.pause_btn = NeonButton(sb, "PAUSE", self.toggle_pause, C["cyan"], self.f_btn, bg, height=44)
        self.pause_btn.pack(fill="x", padx=16, pady=(18, 8))
        NeonButton(sb, "EINSTELLUNGEN", self.open_settings, C["cyan"], self.f_btn, bg).pack(fill="x", padx=16, pady=4)
        self.overlay_btn = NeonButton(sb, "OVERLAY", self.toggle_overlay, C["cyan"], self.f_btn, bg)
        self.overlay_btn.pack(fill="x", padx=16, pady=4)
        NeonButton(sb, "MELDUNGEN LEEREN", self.clear_alerts, C["muted"], self.f_btn, bg).pack(fill="x", padx=16, pady=4)

        def section(title):
            self._label(sb, f"// {title}", fg=C["muted"], font=self.f_btn).pack(anchor="w", padx=18, pady=(20, 6))

        def row(key):
            f = tk.Frame(sb, bg=bg)
            f.pack(fill="x", padx=18, pady=2)
            self._label(f, key, fg=C["muted"], font=self.f_small).pack(side="left")
            v = self._label(f, "–", fg=C["bright"], font=self.f_small)
            v.pack(side="right")
            return v

        section("SCHWELLEN")
        self.thr_lbl = {"CPU": row("CPU"), "RAM": row("RAM"), "Festplatte": row("FESTPLATTE")}
        self.hyst_lbl = row("HYSTERESE")
        self.cool_lbl = row("WARNUNGS-PAUSE")
        section("SYSTEM")
        self.cores_lbl = row("KERNE")
        self.ramtotal_lbl = row("RAM GESAMT")
        self.drive_lbl = row("LAUFWERK")
        self.csv_lbl = row("CSV-PROTOKOLL")
        self.dur_lbl = row("MESSDAUER")

        tk.Frame(sb, bg=bg).pack(fill="both", expand=True)
        tk.Frame(sb, bg=C["line2"], height=1).pack(fill="x", padx=16)
        NeonButton(sb, "BEENDEN", self.quit, C["pink"], self.f_btn, bg).pack(fill="x", padx=16, pady=16)
        return sb

    def _build_main(self, parent) -> tk.Frame:
        main = tk.Frame(parent, bg=C["bg"])
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        # Neon-Reiter für die fünf Ansichten
        nav = tk.Frame(main, bg=C["bg"])
        nav.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        self.nav_btns: list[NeonButton] = []
        for i, title in enumerate(VIEW_TITLES):
            nav.columnconfigure(i, weight=1, uniform="nav")
            b = NeonButton(nav, title, lambda i=i: self.select_view(i), C["muted"], self.f_btn, C["bg"],
                           height=34, width=100)
            b.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 6, 0))
            self.nav_btns.append(b)

        holder = tk.Frame(main, bg=C["bg"])
        holder.grid(row=1, column=0, sticky="nsew")
        holder.columnconfigure(0, weight=1)
        holder.rowconfigure(0, weight=1)
        self.views = [self._build_overview(holder), self._build_drives(holder), self._build_network(holder),
                      self._build_bluetooth(holder), self._build_updates(holder)]
        for v in self.views:
            v.grid(row=0, column=0, sticky="nsew")
            v.grid_remove()
        return main

    # ------------------------------------------------------------ Ansicht Übersicht
    def _build_overview(self, parent) -> tk.Frame:
        view = tk.Frame(parent, bg=C["bg"])
        view.columnconfigure(0, weight=1)
        view.rowconfigure(1, weight=1)
        load = self._panel(view, "AUSLASTUNG")
        load.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        self.bars: dict[str, NeonBar] = {}
        self.pct_lbl: dict[str, tk.Label] = {}
        self.detail_lbl: dict[str, tk.Label] = {}
        for name in METRICS:
            blk = tk.Frame(load.body, bg=C["card"])
            blk.pack(fill="x", padx=16, pady=(10, 2))
            top = tk.Frame(blk, bg=C["card"])
            top.pack(fill="x")
            self._label(top, name.upper(), fg=C["text"], font=self.f_h).pack(side="left", anchor="s")
            self.pct_lbl[name] = self._label(top, "–", fg=C["cyan"], font=self.f_big)
            self.pct_lbl[name].pack(side="right")
            self.bars[name] = NeonBar(blk, C["card"])
            self.bars[name].pack(fill="x", pady=(2, 2))
            self.detail_lbl[name] = self._label(blk, "", fg=C["muted"], font=self.f_small, anchor="w")
            self.detail_lbl[name].pack(fill="x")
        tk.Frame(load.body, bg=C["card"], height=10).pack()

        procs = self._panel(view, "TOP-PROZESSE (NACH CPU)")
        procs.grid(row=1, column=0, sticky="nsew")
        self._small_button(procs.head, "JETZT AKTUALISIEREN", self.refresh_processes, width=190).pack(
            side="right", padx=10, pady=6)
        self.proc_stamp = self._label(procs.head, "Stand –", fg=C["muted"], font=self.f_small)
        self.proc_stamp.pack(side="right", padx=6)
        self.tree = self._tree(procs.body, [("pid", "PID", 70, "e", False), ("name", "NAME", 150, "w", True),
                                            ("cpu", "CPU %", 70, "e", False), ("ram", "RAM %", 70, "e", False),
                                            ("mb", "RAM MB", 80, "e", False)], height=6)
        self.tree.tag_configure("hot", foreground=C["pink"])
        return view

    # ------------------------------------------------------------ Ansicht Laufwerke
    def _build_drives(self, parent) -> tk.Frame:
        view = tk.Frame(parent, bg=C["bg"])
        p = self._panel(view, "LAUFWERKE")
        p.pack(fill="both", expand=True)
        self._small_button(p.head, "AKTUALISIEREN", lambda: self._refresh("drives", force=True)).pack(
            side="right", padx=10, pady=6)
        self.drive_summary = self._label(p.body, "> lese laufwerke …", fg=C["muted"], font=self.f_small,
                                         anchor="w")
        self.drive_summary.pack(fill="x", padx=16, pady=(10, 0))
        self.drive_tree = self._tree(p.body, [
            ("mp", "LAUFWERK", 100, "w", True), ("kind", "TYP", 105, "w", True), ("fs", "FS", 55, "w", False),
            ("used", "BELEGT", 75, "e", False), ("free", "FREI", 72, "e", False),
            ("total", "GESAMT", 80, "e", False), ("pct", "%", 60, "e", False)], height=12)
        self.drive_tree.tag_configure("extern", foreground=C["cyan"])
        self.drive_tree.tag_configure("voll", foreground=C["pink"])
        self._hint(p.body, "Cyan = externes Speichermedium (USB, SD-Karte).  Magenta = Belegung über der "
                           "Festplatten-Schwelle.").pack(fill="x", padx=14, pady=(0, 10))
        return view

    # ------------------------------------------------------------ Ansicht Netzwerk
    def _build_network(self, parent) -> tk.Frame:
        view = tk.Frame(parent, bg=C["bg"])
        view.columnconfigure(0, weight=1)
        view.rowconfigure(1, weight=1)

        w = self._panel(view, "WLAN-VERBINDUNG")
        w.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        self._small_button(w.head, "AKTUALISIEREN", lambda: self._refresh("wlan", force=True)).pack(
            side="right", padx=10, pady=6)
        grid = tk.Frame(w.body, bg=C["card"])
        grid.pack(fill="x", padx=16, pady=(10, 4))
        grid.columnconfigure(1, weight=1)
        self.wlan_labels: dict[str, tk.Label] = {}
        rows = (("adapter", "ADAPTER"), ("state", "STATUS"), ("ssid", "SSID"), ("radio", "STANDARD / BAND"),
                ("rate", "DATENRATE ↓/↑"), ("auth", "SICHERHEIT"))
        for r, (key, text) in enumerate(rows):
            self._label(grid, text, fg=C["muted"], font=self.f_small).grid(row=r, column=0, sticky="w", pady=2)
            lbl = self._label(grid, "–", fg=C["bright"], font=self.f_mono, anchor="w")
            lbl.grid(row=r, column=1, sticky="w", padx=(18, 0), pady=2)
            self.wlan_labels[key] = lbl
        sig = tk.Frame(w.body, bg=C["card"])
        sig.pack(fill="x", padx=16, pady=(4, 2))
        self._label(sig, "SIGNAL", fg=C["text"], font=self.f_h).pack(side="left", anchor="s")
        self.signal_lbl = self._label(sig, "–", fg=C["cyan"], font=self.f_h)
        self.signal_lbl.pack(side="right")
        self.signal_bar = NeonBar(w.body, C["card"], height=10)
        self.signal_bar.pack(fill="x", padx=16)
        self.wlan_hint = self._hint(w.body, fg=C["yellow"])
        self.wlan_hint.pack(fill="x", padx=16, pady=(4, 10))

        t = self._panel(view, "DATENVERKEHR (UP & DOWN)")
        t.grid(row=1, column=0, sticky="nsew")
        top = tk.Frame(t.body, bg=C["card"])
        top.pack(fill="x", padx=16, pady=(10, 0))
        self._label(top, "KARTE", fg=C["muted"], font=self.f_small).pack(side="left")
        self.nic_var = tk.StringVar()
        self.nic_box = ttk.Combobox(top, textvariable=self.nic_var, state="readonly", width=24,
                                    style="Neon.TCombobox", font=self.f_mono)
        self.nic_box.pack(side="left", padx=10)
        self.nic_box.bind("<<ComboboxSelected>>", self._on_nic_selected)
        rates = tk.Frame(t.body, bg=C["card"])
        rates.pack(fill="x", padx=16, pady=(8, 0))
        self.down_label = self._label(rates, "↓ –", fg=C["cyan"], font=self.f_big)
        self.down_label.pack(side="left")
        self.up_label = self._label(rates, "↑ –", fg=C["pink"], font=self.f_big)
        self.up_label.pack(side="left", padx=(28, 0))
        self.total_label = self._label(t.body, "", fg=C["muted"], font=self.f_small, anchor="w")
        self.total_label.pack(fill="x", padx=16)
        self._axis_w = tkfont.Font(font=self.f_small).measure("999.99 MB/s") + 14   # Platz für Achsentext
        self.graph = tk.Canvas(t.body, height=130, bg=C["card"], highlightthickness=1,
                               highlightbackground=C["line"])
        self.graph.pack(fill="both", expand=True, padx=16, pady=(6, 14))
        # neu zeichnen, sobald die Größe bekannt ist bzw. sich ändert
        self.graph.bind("<Configure>", lambda _e: self._draw_graph())
        return view

    # ------------------------------------------------------------ Ansicht Bluetooth
    def _build_bluetooth(self, parent) -> tk.Frame:
        view = tk.Frame(parent, bg=C["bg"])
        p = self._panel(view, "BLUETOOTH")
        p.pack(fill="both", expand=True)
        self._small_button(p.head, "AKTUALISIEREN", lambda: self._refresh("bt", force=True)).pack(
            side="right", padx=10, pady=6)
        self.bt_adapter = self._label(p.body, "> lese bluetooth …", fg=C["muted"], font=self.f_small, anchor="w",
                                      justify="left", wraplength=560)
        self.bt_adapter.pack(fill="x", padx=16, pady=(10, 0))
        self.bt_tree = self._tree(p.body, [("name", "GERÄT", 220, "w", True), ("kind", "TYP", 70, "w", False),
                                           ("conn", "VERBINDUNG", 130, "w", False),
                                           ("pnp", "STATUS", 90, "w", False)], height=12)
        self.bt_tree.tag_configure("on", foreground=C["green"])
        self.bt_tree.tag_configure("off", foreground=C["muted"])
        self._hint(p.body, "Gezeigt werden gekoppelte Geräte. Der Verbindungsstatus stammt aus einer nicht "
                           "dokumentierten Windows-Geräteeigenschaft und kann bei manchen Geräten abweichen. "
                           "Die Abfrage dauert einige Sekunden.").pack(fill="x", padx=14, pady=(0, 10))
        return view

    # ------------------------------------------------------------ Ansicht Updates
    def _build_updates(self, parent) -> tk.Frame:
        view = tk.Frame(parent, bg=C["bg"])
        p = self._panel(view, "UPDATES (WINGET)")
        p.pack(fill="both", expand=True)
        btns = tk.Frame(p.body, bg=C["card"])
        btns.pack(fill="x", padx=16, pady=(10, 0))
        self.upd_btn = self._small_button(btns, "SUCHEN", self.check_updates, width=110)
        self.upd_btn.pack(side="left")
        self._small_button(btns, "AUSGEWÄHLTE", self.install_updates, width=130).pack(side="left", padx=8)
        self._small_button(btns, "ALLE", lambda: self.install_updates(all_=True), C["pink"], width=90).pack(
            side="left")
        self.upd_status = self._label(p.body, "> noch nicht gesucht", fg=C["muted"], font=self.f_small, anchor="w")
        self.upd_status.pack(fill="x", padx=16, pady=(8, 0))
        self.upd_tree = self._tree(p.body, [
            ("name", "NAME", 160, "w", True), ("id", "ID", 150, "w", True), ("inst", "ALT", 85, "w", False),
            ("avail", "NEU", 85, "w", False), ("src", "QUELLE", 75, "w", False)],
            height=12, selectmode="extended")
        self._hint(p.body, "Die Aktualisierung läuft in einem eigenen Konsolenfenster über winget. Manche "
                           "Programme fragen dabei per Benutzerkontensteuerung nach Administratorrechten.").pack(
            fill="x", padx=14, pady=(0, 10))
        return view

    # ------------------------------------------------------------ rechte Spalte
    def _build_right(self, parent) -> tk.Frame:
        right = tk.Frame(parent, bg=C["bg"], width=330)
        right.grid_propagate(False)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        al = self._panel(right, "MELDUNGEN")
        al.grid(row=0, column=0, sticky="nsew", pady=(0, 18))
        self.alert_count_lbl = self._label(al.head, "0", fg=C["pink"], font=self.f_btn)
        self.alert_count_lbl.pack(side="right", padx=14)
        wrap = tk.Frame(al.body, bg=C["card"])
        wrap.pack(fill="both", expand=True, padx=8, pady=8)
        self.alert_list = tk.Listbox(wrap, font=self.f_small, bg=C["card"], fg=C["text"], bd=0,
                                     highlightthickness=0, selectbackground=C["select"],
                                     selectforeground=C["bright"], activestyle="none")
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.alert_list.yview,
                           style="Neon.Vertical.TScrollbar")
        self.alert_list.configure(yscrollcommand=sb.set)
        self.alert_list.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        lg = self._panel(right, "LEGENDE")
        lg.grid(row=1, column=0, sticky="ew")
        for color, text in ((C["cyan"], "normal / extern"),
                            (C["yellow"], "max. 10 Pkt. unter Schwelle"),
                            (C["pink"], "Schwelle erreicht / Upload"),
                            (C["green"], "OK / verbunden"),
                            (C["bright"], "Strich = Warnschwelle")):
            f = tk.Frame(lg.body, bg=C["card"])
            f.pack(fill="x", padx=14, pady=3)
            tk.Frame(f, bg=color, width=12, height=12).pack(side="left", padx=(0, 10))
            self._label(f, text, fg=C["text"], font=self.f_small).pack(side="left")
        tk.Frame(lg.body, bg=C["card"], height=8).pack()
        return right

    # ================================================================== Ansichten wechseln
    def select_view(self, index: int) -> None:
        self.views[self._view].grid_remove()
        self._view = index
        self.views[index].grid()
        for i, b in enumerate(self.nav_btns):
            b.set(color=C["cyan"] if i == index else C["muted"], active=(i == index))
        self._on_view_changed()

    def current_view(self) -> int:
        return self._view

    def _on_view_changed(self) -> None:
        v = self._view
        if v == TAB_OVERVIEW and self._last_snapshot is not None:
            self._show_snapshot(self._last_snapshot)
        elif v == TAB_NETWORK:
            self._refresh("wlan")
            self._show_traffic_labels()
            self.root.after_idle(self._draw_graph)
        elif v == TAB_BT:
            self._refresh("bt")
        elif v == TAB_UPDATES and not self._updates_checked:
            self.check_updates()

    _last_snapshot: Snapshot | None = None

    # ================================================================== Ablauf
    def _minimized(self) -> bool:
        """Minimiert oder versteckt (z. B. wegen Overlay): dann wird im Hauptfenster nichts gezeichnet."""
        try:
            return self.root.state() in ("iconic", "withdrawn")
        except tk.TclError:
            return True

    def _measure(self, skip_processes: bool):
        """Läuft im Hintergrund-Thread: Messung und Netzwerkzähler lesen (psutil, ~6 ms unter Windows)."""
        return self.monitor.step(skip_processes=skip_processes), self.meter.read()

    def _tick(self) -> None:
        """Wird alle interval_s Sekunden über root.after() aufgerufen.
        Die Messung läuft im Hintergrund-Thread; ist die vorige noch nicht fertig, wird diese Runde übersprungen."""
        self._job = None
        try:
            hidden = self._minimized()
            skip = hidden or self._view != TAB_OVERVIEW      # Prozessliste nur, wenn man sie sieht
            self.runner.submit("measure", lambda: self._measure(skip),
                               lambda res: self._handle("Messung", res, self._show_measurement))
            if not hidden:
                self._refresh("drives")                  # psutil, schnell -> immer (für USB-Meldungen)
                if self._view == TAB_NETWORK:
                    self._refresh("wlan")                # netsh nur bei geöffneter Ansicht
                elif self._view == TAB_BT:
                    self._refresh("bt")                  # PowerShell nur bei geöffneter Ansicht
        except Exception as exc:
            log.exception("Fehler im Zyklus")
            self._set(self.status, f"> FEHLER: {exc}", fg=C["pink"])
        if not self.paused:
            self._job = self.root.after(int(self.monitor.config.interval_s * 1000), self._tick)

    def _on_restore(self, event) -> None:
        """Fenster wieder sichtbar -> sofort aktuelle Werte statt bis zum nächsten Takt warten."""
        if event.widget is self.root and not self.paused and self._job:
            self.root.after_cancel(self._job)
            self._job = self.root.after(50, self._tick)

    def _poll_background(self) -> None:
        self.runner.poll()
        try:
            while True:                                  # globales Tastenkürzel (kommt aus eigenem Thread)
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
            self._set(self.status, f"> {key}: fehler – {result}", fg=C["pink"])
            return
        callback(result)

    # ------------------------------------------------------------ Meldungen
    def _add_message(self, text: str, color: str, bell: bool = False) -> None:
        lb = self.alert_list
        lb.insert("end", text)
        lb.itemconfig("end", foreground=color)
        if lb.size() > MAX_ALERTS:
            lb.delete(0, lb.size() - MAX_ALERTS - 1)
        lb.see("end")
        self._alert_count += 1
        self._set(self.alert_count_lbl, str(self._alert_count))
        if bell:
            self.root.bell()

    def _add_alert(self, a) -> None:
        if a.level is Level.WARNUNG:      # kompakte Form, passt in die Spalte
            self._add_message(f"{a.timestamp:%H:%M:%S}  WARN  {a.metric} {a.value:.1f} % (≥ {a.threshold:.0f})",
                              C["pink"], bell=True)
        else:
            self._add_message(f"{a.timestamp:%H:%M:%S}  OK    {a.metric} {a.value:.1f} %", C["green"])

    def clear_alerts(self) -> None:
        self.alert_list.delete(0, "end")
        self._alert_count = 0
        self._set(self.alert_count_lbl, "0")

    # ------------------------------------------------------------ Anzeige Übersicht
    def _show_measurement(self, result) -> None:
        (snap, alerts), counters = result
        self._last_snapshot = snap
        for a in alerts:
            self._add_alert(a)
        self._update_traffic(counters)                    # Rate immer berechnen (Verlauf und Overlay)
        self._update_overlay()
        if self._minimized():
            return
        cfg = self.monitor.config
        self._set(self.uptime_lbl, format_uptime(snap.uptime_s))
        self._set(self.interval_lbl, f"{cfg.interval_s:g} s")
        self._set(self.dur_lbl, f"{self.monitor.last_duration_s * 1000:.0f} ms")
        for name, lbl in self.thr_lbl.items():
            self._set(lbl, f"{cfg.thresholds()[name]:.0f} %")
        self._set(self.hyst_lbl, f"{cfg.hysteresis:g} Pkt.")
        self._set(self.cool_lbl, f"{cfg.alert_cooldown_s} s")
        self._set(self.cores_lbl, str(snap.cpu_cores))
        self._set(self.ramtotal_lbl, f"{snap.ram_total_gb:.1f} GB")
        self._set(self.drive_lbl, snap.disk_path)
        self._set(self.csv_lbl, "AN" if cfg.csv_logging else "AUS")
        if self._view == TAB_OVERVIEW:                    # Balken/Tabelle nur zeichnen, wenn sichtbar
            self._show_snapshot(snap)
        if not self.paused:
            self._set(self.status, f"> letzte Messung {snap.timestamp:%H:%M:%S}   ·   "
                                   f"messdauer {self.monitor.last_duration_s * 1000:.0f} ms   ·   "
                                   f"{len(snap.processes)} prozesse", fg=C["muted"])

    @staticmethod
    def _state(value: float, threshold: float) -> str:
        if value >= threshold:
            return "alarm"
        if value >= threshold - 10:
            return "nah"
        return "normal"

    def _show_snapshot(self, s: Snapshot) -> None:
        thresholds = self.monitor.config.thresholds()
        values = {
            "CPU": (s.cpu_percent, f"{s.cpu_cores} logische Kerne"),
            "RAM": (s.ram_percent, f"{s.ram_used_gb:.1f} / {s.ram_total_gb:.1f} GB belegt"),
            "Festplatte": (s.disk_percent,
                           f"{s.disk_used_gb:.0f} / {s.disk_total_gb:.0f} GB belegt  ·  {s.disk_path}"),
        }
        for name, (pct, detail) in values.items():
            color = STATE_COLOR[self._state(pct, thresholds[name])]
            self.bars[name].set(pct, thresholds[name], color)
            lbl = self.pct_lbl[name]
            text = f"{pct:.1f} %"
            if self._texts.get(id(lbl)) != text or lbl.cget("fg") != color:
                self._texts[id(lbl)] = text
                lbl.config(text=text, fg=color)
            self._set(self.detail_lbl[name], detail)
        if s.processes is not self._last_processes:       # Prozessliste unverändert -> nichts tun
            self._last_processes = s.processes
            self._update_tree(s)
            self._set(self.proc_stamp, f"Stand {s.timestamp:%H:%M:%S}", fg=C["muted"])

    def _update_tree(self, s: Snapshot) -> None:
        """Vorhandene Zeilen wiederverwenden, nur geänderte Werte schreiben."""
        cpu_limit = self.monitor.config.cpu_threshold
        for i, p in enumerate(s.processes):
            vals = (p.pid, p.name, f"{p.cpu_percent:.1f}", f"{p.memory_percent:.1f}", f"{p.memory_mb:.0f}")
            tags = ("hot",) if p.cpu_percent >= cpu_limit else (("odd",) if i % 2 else ())
            key = (vals, tags)
            if i < len(self._rows):
                if self._row_vals[i] != key:
                    self.tree.item(self._rows[i], values=vals, tags=tags)
                    self._row_vals[i] = key
            else:
                self._rows.append(self.tree.insert("", "end", values=vals, tags=tags))
                self._row_vals.append(key)
        n = len(s.processes)
        if len(self._rows) > n:
            self.tree.delete(*self._rows[n:])
            del self._rows[n:], self._row_vals[n:]

    # ------------------------------------------------------------ Anzeige Laufwerke
    def _show_drives(self, drives: list[DriveInfo]) -> None:
        limit = self.monitor.config.disk_threshold
        self.drive_tree.delete(*self.drive_tree.get_children())
        for i, d in enumerate(drives):
            tags = ("voll",) if d.percent >= limit else ("extern",) if d.external else (("odd",) if i % 2 else ())
            self.drive_tree.insert("", "end", tags=tags, values=(
                d.mountpoint, d.kind, d.fstype, f"{d.used_gb:.1f} GB", f"{d.free_gb:.1f} GB",
                f"{d.total_gb:.1f} GB", f"{d.percent:.1f} %"))
        external = {d.mountpoint for d in drives if d.external}
        self._set(self.drive_summary, f"> {len(drives)} laufwerk(e)   ·   {len(external)} extern   ·   "
                                      f"stand {datetime.now():%H:%M:%S}")
        if self._external is not None:                  # beim ersten Einlesen nicht melden
            zeit = datetime.now().strftime("%H:%M:%S")
            for mp in sorted(external - self._external):
                self._add_message(f"{zeit}  USB   angeschlossen: {mp}", C["cyan"])
                log.info("Externes Laufwerk angeschlossen: %s", mp)
            for mp in sorted(self._external - external):
                self._add_message(f"{zeit}  USB   entfernt: {mp}", C["cyan"])
                log.info("Externes Laufwerk entfernt: %s", mp)
        self._external = external

    # ------------------------------------------------------------ Anzeige WLAN / Traffic
    def _show_wlan(self, status: WlanStatus) -> None:
        self._set(self.wlan_hint, status.message)
        info = next((i for i in status.interfaces if i.connected), status.interfaces[0] if status.interfaces else None)
        if info is None:
            for lbl in self.wlan_labels.values():
                self._set(lbl, "–")
            self.signal_bar.set(0, None, C["dim"])
            self._set(self.signal_lbl, "–")
            return
        band = " / ".join(x for x in (info.radio, info.band, f"Kanal {info.channel}" if info.channel else "") if x)
        rate = " / ".join(x for x in (info.rx_mbit, info.tx_mbit) if x)
        # netsh liefert reine Zahlen (MBit/s), Get-NetAdapter Text wie "866.7 Mbps"
        has_unit = any(ch.isalpha() for ch in rate)
        self._set(self.wlan_labels["adapter"], f"{info.name}  ({info.description})" if info.description else info.name)
        self._set(self.wlan_labels["state"], (info.state or "–").upper(),
                  fg=C["green"] if info.connected else C["pink"])
        self._set(self.wlan_labels["ssid"], info.ssid or "– (nicht lesbar)")
        self._set(self.wlan_labels["radio"], band or "–")
        self._set(self.wlan_labels["rate"], (rate if has_unit else f"{rate} MBit/s") if rate else "–")
        self._set(self.wlan_labels["auth"], info.auth or "–")
        sig = info.signal or 0
        color = C["cyan"] if sig >= 60 else C["yellow"] if sig >= 30 else C["pink"]
        self.signal_bar.set(sig, None, color)
        self._set(self.signal_lbl, f"{info.signal} %" if info.signal is not None else "–", fg=color)
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
        """Rate berechnen (immer) und anzeigen (nur wenn die Ansicht Netzwerk sichtbar ist)."""
        names = self.meter.interfaces(counters)
        if names != self._nic_names:                     # Auswahlliste nur bei Änderung neu setzen
            self._nic_names = names
            self.nic_box["values"] = names
        nic = self.nic_var.get()
        self._last_sample = self.meter.sample(nic, counters) if nic else None   # immer messen (Verlauf)
        self._last_nic = nic
        if self._view != TAB_NETWORK or self._minimized():
            return                                       # nur sichtbare Ansicht zeichnen
        self._show_traffic_labels()
        self._draw_graph()

    def _show_traffic_labels(self) -> None:
        sample, nic = self._last_sample, self._last_nic
        if sample is None:
            self._set(self.down_label, "↓ –")
            self._set(self.up_label, "↑ –")
            self._set(self.total_label, "keine netzwerkkarte gewählt" if not nic else f"'{nic}' nicht gefunden")
            return
        self._set(self.down_label, f"↓ {format_rate(sample.down_bps)}")
        self._set(self.up_label, f"↑ {format_rate(sample.up_bps)}")
        self._set(self.total_label, f"seit programmstart:  ↓ {format_bytes(sample.total_down)}   "
                                    f"↑ {format_bytes(sample.total_up)}")

    def _draw_graph(self) -> None:
        c = self.graph
        w, h = c.winfo_width(), c.winfo_height()
        if w < 150 or h < 80:            # Ansicht nicht sichtbar -> Größe noch unbekannt
            return
        c.delete("all")
        left, top, bottom = self._axis_w, 12, 22
        data = list(self.meter.history)
        peak = max([max(d, u) for d, u in data] + [1024.0])
        for i in range(5):                                    # Gitterlinien mit Beschriftung
            y = top + (h - top - bottom) * i / 4
            c.create_line(left, y, w - 8, y, fill=C["line"])
            c.create_text(left - 8, y, text=format_rate(peak * (4 - i) / 4), anchor="e",
                          fill=C["dim"], font=self.f_small)
        c.create_text(left, h - 6, text=f"letzte {len(data)} messungen", anchor="sw", fill=C["dim"],
                      font=self.f_small)
        c.create_text(w - 8, h - 6, text="↓ download   ↑ upload", anchor="se", fill=C["dim"], font=self.f_small)
        if len(data) < 2:
            return
        step = (w - 8 - left) / (self.meter.history.maxlen - 1)
        x0 = w - 8 - step * (len(data) - 1)
        for idx, color in ((0, C["cyan"]), (1, C["pink"])):
            pts = []
            for k, values in enumerate(data):
                pts += [x0 + k * step, top + (h - top - bottom) * (1 - values[idx] / peak)]
            c.create_line(*pts, fill=blend(color, C["card"], 0.25), width=6)     # Leuchtsaum
            c.create_line(*pts, fill=color, width=2)

    # ------------------------------------------------------------ Anzeige Bluetooth
    def _show_bluetooth(self, status: BluetoothStatus) -> None:
        if status.adapters:
            text = "> adapter: " + ", ".join(f"{n} ({s})" for n, s in status.adapters)
        else:
            text = "> " + (status.message or "kein bluetooth-adapter gefunden")
        connected = sum(1 for d in status.devices if d.connected)
        if status.devices:
            text += f"   ·   {len(status.devices)} gekoppelt, {connected} verbunden"
        self._set(self.bt_adapter, text)
        self.bt_tree.delete(*self.bt_tree.get_children())
        for d in status.devices:
            self.bt_tree.insert("", "end", tags=("on" if d.connected else "off",),
                                values=(d.name, d.kind, d.connection_text.upper(), d.status))

    # ------------------------------------------------------------ Updates
    def check_updates(self) -> None:
        self._updates_checked = True
        if self.runner.submit("updates", list_updates, lambda r: self._handle("updates", r, self._show_updates)):
            self._set(self.upd_status, "> suche updates mit winget … (kann bis zu einer minute dauern)",
                      fg=C["yellow"])
            self.upd_btn.set(color=C["dim"])

    def _show_updates(self, result: UpdateResult) -> None:
        self.upd_btn.set(color=C["cyan"])
        self.upd_tree.delete(*self.upd_tree.get_children())
        for i, u in enumerate(result.updates):
            self.upd_tree.insert("", "end", iid=u.package_id, tags=(("odd",) if i % 2 else ()),
                                 values=(u.name, u.package_id, u.installed, u.available, u.source))
        self._set(self.upd_status, f"> {result.message}   ({datetime.now():%H:%M})", fg=C["muted"])
        self.nav_btns[TAB_UPDATES].set(text=f"UPDATES ({len(result.updates)})" if result.updates else "UPDATES")

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
            self._set(self.upd_status, "> aktualisierung im konsolenfenster gestartet – danach erneut suchen",
                      fg=C["green"])
        except Exception as exc:
            messagebox.showerror("Updates", str(exc), parent=self.root)

    def refresh_processes(self) -> None:
        """Prozessliste sofort neu erstellen (Knopf). Sie wird sonst nur alle process_interval_s Sekunden erstellt,
        und nur, solange die Ansicht Übersicht sichtbar ist (der Scan dauert unter Windows mehrere Sekunden)."""
        if self._minimized() or self._view != TAB_OVERVIEW:
            return
        self.monitor.collector.invalidate_processes()
        self._set(self.proc_stamp, "wird erstellt …", fg=C["yellow"])
        self.runner.submit("measure", lambda: self._measure(False),
                           lambda res: self._handle("Messung", res, self._show_measurement))

    # ================================================================== Overlay
    def toggle_overlay(self) -> None:
        """Overlay ein-/ausschalten (Knopf oder Tastenkürzel). Das Hauptfenster wird nur versteckt,
        wenn das Tastenkürzel funktioniert – sonst käme man nicht mehr zurück."""
        cfg = self.monitor.config
        if self.overlay is None:
            self.overlay = OverlayWindow(self.root, cfg, (self.f_mono[0], 10, "bold"), C, STATE_COLOR)
        ov = self.overlay
        if ov.visible:
            ov.hide()
            self.overlay_btn.set("OVERLAY", C["cyan"], active=False)
            if self._hidden_for_overlay:
                self._hidden_for_overlay = False
                self.root.deiconify()
            return
        ov.apply_config(cfg)
        ov.show()
        self.overlay_btn.set("OVERLAY AUS", C["yellow"], active=True)
        self._update_overlay()
        if cfg.overlay_hide_main:
            if self._hotkey_ok:
                self._hidden_for_overlay = True
                self.root.withdraw()
            else:
                self._set(self.status, f"> overlay an – hauptfenster bleibt sichtbar, weil das tastenkürzel "
                                       f"{cfg.overlay_hotkey} nicht verfügbar ist", fg=C["yellow"])

    def _update_overlay(self) -> None:
        ov, snap = self.overlay, self._last_snapshot
        if ov is None or not ov.visible or snap is None:
            return
        cfg, sample = self.monitor.config, self._last_sample
        ov.update(OverlayData(
            snap.cpu_percent, snap.ram_percent, sample.down_bps if sample else 0.0, sample.up_bps if sample else 0.0,
            f"{snap.timestamp:%H:%M}",
            (level_for(snap.cpu_percent, cfg.cpu_threshold), level_for(snap.ram_percent, cfg.ram_threshold),
             level_for(snap.disk_percent, cfg.disk_threshold))))

    # ================================================================== Aktionen
    def toggle_pause(self) -> None:
        if self.paused:
            self.paused = False
            self.pause_btn.set("PAUSE", C["cyan"])
            self.state_lbl.config(text="LIVE", fg=C["green"])
            self.dot.itemconfig(self._dot, fill=C["green"])
            self._tick()
        else:
            self.paused = True
            if self._job:
                self.root.after_cancel(self._job)
                self._job = None
            self.pause_btn.set("FORTSETZEN", C["yellow"])
            self.state_lbl.config(text="PAUSE", fg=C["yellow"])
            self.dot.itemconfig(self._dot, fill=C["yellow"])
            self._set(self.status, "> pausiert", fg=C["yellow"])

    def open_settings(self) -> None:
        SettingsDialog(self, self.monitor.config, self._apply_settings)

    def _apply_settings(self, new_cfg: Config) -> None:
        old_hotkey = self.monitor.config.overlay_hotkey
        new_cfg.save(self.config_path)
        self.monitor.apply_config(new_cfg)
        if self.overlay is not None:
            self.overlay.apply_config(new_cfg)
            self._update_overlay()
        log.info("Einstellungen geändert: %s", new_cfg)
        note = "  ·  neues tastenkürzel gilt nach neustart" if new_cfg.overlay_hotkey != old_hotkey else ""
        self._set(self.status, "> einstellungen gespeichert" + note, fg=C["green"])

    def quit(self) -> None:
        if self._job:
            self.root.after_cancel(self._job)
            self._job = None
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

    def __init__(self, app: MonitorApp, config: Config, on_save) -> None:
        super().__init__(app.root)
        self.title("EINSTELLUNGEN")
        bg = C["panel"]
        self.configure(bg=bg, highlightthickness=1, highlightbackground=C["cyan"])
        self.resizable(False, False)
        self.transient(app.root)
        self.config_obj = config
        self.on_save = on_save
        self.vars: dict[str, tk.StringVar] = {}

        tk.Label(self, text="// EINSTELLUNGEN", fg=C["cyan"], bg=bg, font=app.f_h).grid(
            row=0, column=0, columnspan=4, sticky="w", padx=18, pady=(16, 10))
        tk.Label(self, text="// OVERLAY", fg=C["cyan"], bg=bg, font=app.f_h).grid(
            row=0, column=2, columnspan=2, sticky="w", padx=(30, 18), pady=(16, 10))

        def label(text, row, col):
            tk.Label(self, text=text, fg=C["text"], bg=bg, font=app.f_mono).grid(
                row=row, column=col, sticky="w", padx=(18 if col == 0 else 30, 8), pady=3)

        # linke Spalte: Messung und Schwellen
        left = [f for f in self.FIELDS if f[0] != "overlay_alpha"]
        for row, (key, text, lo, hi, step) in enumerate(left, start=1):
            label(text, row, 0)
            var = tk.StringVar(value=str(getattr(config, key)))
            ttk.Spinbox(self, from_=lo, to=hi, increment=step, textvariable=var, width=10,
                        style="Neon.TSpinbox", font=app.f_mono).grid(row=row, column=1, padx=(0, 8), pady=3)
            self.vars[key] = var
        row = len(left) + 1
        label("Laufwerk/Pfad (leer = System)", row, 0)
        self.disk_var = tk.StringVar(value=config.disk_path)
        ttk.Entry(self, textvariable=self.disk_var, width=12, style="Neon.TEntry",
                  font=app.f_mono).grid(row=row, column=1, padx=(0, 8), pady=3)
        self.bool_vars: dict[str, tk.BooleanVar] = {}

        def check(key, text, row, col, span):
            self.bool_vars[key] = tk.BooleanVar(value=bool(getattr(config, key)))
            tk.Checkbutton(self, text=text, variable=self.bool_vars[key], fg=C["text"], bg=bg,
                           activebackground=bg, activeforeground=C["bright"], selectcolor=C["track"],
                           font=app.f_mono, highlightthickness=0, bd=0).grid(
                row=row, column=col, columnspan=span, sticky="w", padx=(14 if col == 0 else 26, 0), pady=(2, 0))

        check("check_updates_on_start", "Sofort beim Start nach Updates suchen", row + 1, 0, 2)
        last_left = row + 1

        # rechte Spalte: Overlay
        r = 1
        label("Deckkraft (0,2 – 1)", r, 2)
        self.vars["overlay_alpha"] = tk.StringVar(value=str(config.overlay_alpha))
        ttk.Spinbox(self, from_=0.2, to=1.0, increment=0.05, textvariable=self.vars["overlay_alpha"], width=10,
                    style="Neon.TSpinbox", font=app.f_mono).grid(row=r, column=3, padx=(0, 18), pady=3)
        self.choice_vars: dict[str, tk.StringVar] = {}
        for key, text, values in (("overlay_style", "Stil", OVERLAY_STYLES), ("overlay_position", "Position", POSITIONS)):
            r += 1
            label(text, r, 2)
            self.choice_vars[key] = tk.StringVar(value=str(getattr(config, key)))
            ttk.Combobox(self, textvariable=self.choice_vars[key], values=values, state="readonly", width=12,
                         style="Neon.TCombobox", font=app.f_mono).grid(row=r, column=3, padx=(0, 18), pady=3)
        r += 1
        label("Tastenkürzel (nach Neustart)", r, 2)
        self.hotkey_var = tk.StringVar(value=config.overlay_hotkey)
        ttk.Entry(self, textvariable=self.hotkey_var, width=14, style="Neon.TEntry",
                  font=app.f_mono).grid(row=r, column=3, padx=(0, 18), pady=3)
        for key, text in (("overlay_enabled", "beim Start anzeigen"),
                          ("overlay_click_through", "Mausklicks gehen hindurch"),
                          ("overlay_hide_main", "Hauptfenster verstecken")):
            r += 1
            check(key, text, r, 2, 2)

        btns = tk.Frame(self, bg=bg)
        btns.grid(row=max(last_left, r) + 1, column=0, columnspan=4, pady=(14, 18), padx=18, sticky="ew")
        btns.columnconfigure((0, 1), weight=1)
        NeonButton(btns, "SPEICHERN", self._save, C["cyan"], app.f_btn, bg,
                   width=160).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        NeonButton(btns, "ABBRECHEN", self.destroy, C["muted"], app.f_btn, bg,
                   width=160).grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self.bind("<Escape>", lambda e: self.destroy())

        # mittig über dem Hauptfenster öffnen
        self.update_idletasks()
        root = app.root
        x = root.winfo_rootx() + (root.winfo_width() - self.winfo_reqwidth()) // 2
        y = root.winfo_rooty() + (root.winfo_height() - self.winfo_reqheight()) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        self.grab_set()   # Dialog ist modal

    def _save(self) -> None:
        try:
            changes = {}
            for key, *_ in self.FIELDS:
                value = float(self.vars[key].get().replace(",", "."))
                changes[key] = int(value) if key in self.INT_FIELDS else value
            changes["disk_path"] = self.disk_var.get().strip()
            for key, var in self.choice_vars.items():
                changes[key] = var.get()
            changes["overlay_hotkey"] = self.hotkey_var.get().strip()
            for key, var in self.bool_vars.items():
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
    sys.setswitchinterval(0.001)
    root = tk.Tk()
    MonitorApp(root, monitor, config_path)
    root.mainloop()
