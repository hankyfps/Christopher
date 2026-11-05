"""Grafische Oberfläche mit tkinter (Tabs: Übersicht, Laufwerke, Netzwerk, Bluetooth, Updates)."""
from __future__ import annotations

import logging
import sys
import time
import tkinter as tk
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
from .tasks import BackgroundRunner
from .updates import UpdateResult, list_updates, start_upgrade
from .winutil import IS_WINDOWS

log = logging.getLogger("monitor.gui")

METRICS = ("CPU", "RAM", "Festplatte")
TAB_OVERVIEW, TAB_DRIVES, TAB_NETWORK, TAB_BT, TAB_UPDATES = range(5)
RED, GREEN, BLUE, ORANGE, GREY = "#d93025", "#2e7d32", "#1a5fb4", "#e66100", "#666666"


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
        self._last_processes: tuple = ()
        self._updates_checked = False

        root.title("System-Monitor")
        root.geometry("880x680")
        root.minsize(720, 560)
        root.protocol("WM_DELETE_WINDOW", self.quit)

        self._setup_styles()
        self._build_widgets()
        self._choose_initial_nic()
        self._job = root.after(500, self._tick)
        root.after(100, self._poll_background)
        if monitor.config.check_updates_on_start:
            root.after(3000, self.check_updates)

    # ================================================================== Aufbau
    def _setup_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")       # 'clam' erlaubt farbige Fortschrittsbalken
        for name, color in (("gruen", "#2e9e44"), ("gelb", "#e0a800"), ("rot", RED)):
            style.configure(f"{name}.Horizontal.TProgressbar", background=color,
                            troughcolor="#e6e6e6", thickness=20)

    def _build_widgets(self) -> None:
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=6, pady=(6, 0))
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

        frm_b = ttk.Frame(self.root)
        frm_b.pack(fill="x", padx=6, pady=4)
        self.pause_btn = ttk.Button(frm_b, text="Pause", command=self.toggle_pause)
        self.pause_btn.pack(side="left")
        ttk.Button(frm_b, text="Einstellungen", command=self.open_settings).pack(side="left", padx=6)
        ttk.Button(frm_b, text="Beenden", command=self.quit).pack(side="right")

        self.status = ttk.Label(self.root, text="Starte …", relief="sunken", anchor="w")
        self.status.pack(fill="x", side="bottom")

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
        frm = ttk.LabelFrame(tab, text="Auslastung")
        frm.pack(fill="x", **pad)
        frm.columnconfigure(1, weight=1)
        self.bars: dict[str, ttk.Progressbar] = {}
        self.value_labels: dict[str, ttk.Label] = {}
        for row, name in enumerate(METRICS):
            ttk.Label(frm, text=name, width=11).grid(row=row, column=0, sticky="w", **pad)
            bar = ttk.Progressbar(frm, maximum=100, style="gruen.Horizontal.TProgressbar")
            bar.grid(row=row, column=1, sticky="ew", **pad)
            lbl = ttk.Label(frm, text="–", width=36)
            lbl.grid(row=row, column=2, sticky="w", **pad)
            self.bars[name] = bar
            self.value_labels[name] = lbl
        self.info_label = ttk.Label(frm, text="")
        self.info_label.grid(row=len(METRICS), column=0, columnspan=3, sticky="w", **pad)

        frm_p = ttk.LabelFrame(tab, text="Top-Prozesse (nach CPU)")
        frm_p.pack(fill="both", expand=True, **pad)
        box, self.tree = self._tree(frm_p, [("pid", "PID", 70, "e"), ("name", "Name", 280, "w"),
                                            ("cpu", "CPU %", 80, "e"), ("ram", "RAM %", 80, "e"),
                                            ("mb", "RAM MB", 90, "e")], height=7)
        box.pack(fill="both", expand=True, padx=4, pady=4)

        frm_a = ttk.LabelFrame(tab, text="Meldungen")
        frm_a.pack(fill="both", **pad)
        self.alert_list = tk.Listbox(frm_a, height=6, font=("Consolas", 9))
        sb = ttk.Scrollbar(frm_a, orient="vertical", command=self.alert_list.yview)
        self.alert_list.configure(yscrollcommand=sb.set)
        self.alert_list.pack(side="left", fill="both", expand=True, padx=(4, 0), pady=4)
        sb.pack(side="right", fill="y", pady=4)
        ttk.Button(tab, text="Meldungen leeren",
                   command=lambda: self.alert_list.delete(0, "end")).pack(anchor="e", padx=8)

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
        self.signal_bar = ttk.Progressbar(sig_frame, maximum=100, length=220, style="gruen.Horizontal.TProgressbar")
        self.signal_bar.pack(side="left")
        self.signal_label = ttk.Label(sig_frame, text="–")
        self.signal_label.pack(side="left", padx=8)
        self.wlan_hint = ttk.Label(frm_w, text="", foreground=ORANGE, wraplength=780, justify="left")
        self.wlan_hint.grid(row=r + 1, column=0, columnspan=3, sticky="w", **pad)
        ttk.Button(frm_w, text="Aktualisieren",
                   command=lambda: self._refresh("wlan", force=True)).grid(row=0, column=3, sticky="e", **pad)

        frm_t = ttk.LabelFrame(tab, text="Datenverkehr (Up & Down)")
        frm_t.pack(fill="both", expand=True, padx=8, pady=6)
        top = ttk.Frame(frm_t)
        top.pack(fill="x", padx=6, pady=4)
        ttk.Label(top, text="Netzwerkkarte:").pack(side="left")
        self.nic_var = tk.StringVar()
        self.nic_box = ttk.Combobox(top, textvariable=self.nic_var, state="readonly", width=34)
        self.nic_box.pack(side="left", padx=6)
        self.nic_box.bind("<<ComboboxSelected>>", self._on_nic_selected)
        self.down_label = ttk.Label(top, text="↓ –", foreground=BLUE, font=("Segoe UI", 11, "bold"))
        self.down_label.pack(side="left", padx=(20, 10))
        self.up_label = ttk.Label(top, text="↑ –", foreground=ORANGE, font=("Segoe UI", 11, "bold"))
        self.up_label.pack(side="left")
        self.total_label = ttk.Label(frm_t, text="", foreground=GREY)
        self.total_label.pack(anchor="w", padx=6)
        self.graph = tk.Canvas(frm_t, height=170, background="white", highlightthickness=1,
                               highlightbackground="#cccccc")
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
        self.bt_hint = ttk.Label(tab, foreground=GREY, wraplength=820, justify="left", text=(
            "Gezeigt werden gekoppelte Geräte. Der Verbindungsstatus stammt aus einer nicht dokumentierten "
            "Windows-Geräteeigenschaft und kann bei manchen Geräten abweichen. Die Abfrage dauert einige Sekunden."))
        self.bt_hint.pack(anchor="w", padx=8, pady=(0, 6))

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
        ttk.Label(tab, foreground=GREY, wraplength=820, justify="left", text=(
            "Die Aktualisierung läuft in einem eigenen Konsolenfenster über winget. Manche Programme fragen dabei "
            "per Benutzerkontensteuerung nach Administratorrechten.")).pack(anchor="w", padx=8, pady=(0, 6))

    # ================================================================== Ablauf
    def _tick(self) -> None:
        """Wird alle interval_s Sekunden über root.after() aufgerufen.
        Die eigentliche Messung läuft im Hintergrund-Thread, damit das Fenster nie einfriert.
        Ist die vorige Messung noch nicht fertig, wird diese Runde übersprungen."""
        try:
            self.runner.submit("measure", self.monitor.step,
                               lambda res: self._handle("Messung", res, self._show_measurement))
            self._update_traffic()
            self._refresh("drives")                      # psutil, schnell -> immer (für USB-Meldungen)
            tab = self._current_tab()
            if tab == TAB_NETWORK:
                self._refresh("wlan")                    # netsh nur bei geöffnetem Tab
            elif tab == TAB_BT:
                self._refresh("bt")                      # PowerShell nur bei geöffnetem Tab
        except Exception as exc:
            log.exception("Fehler im Zyklus")
            self.status.config(text=f"Fehler: {exc}")
        self._job = self.root.after(int(self.monitor.config.interval_s * 1000), self._tick)

    def _show_measurement(self, result) -> None:
        snap, alerts = result
        self._show_snapshot(snap)
        for a in alerts:
            self._add_message(a.message(), RED if a.level is Level.WARNUNG else GREEN,
                              bell=a.level is Level.WARNUNG)
        self.status.config(text=f"Letzte Messung: {snap.timestamp:%H:%M:%S}   "
                                f"Intervall: {self.monitor.config.interval_s:g} s   "
                                f"Messdauer: {self.monitor.last_duration_s * 1000:.0f} ms")

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

    def _poll_background(self) -> None:
        self.runner.poll()
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
        self.alert_list.insert("end", text)
        self.alert_list.itemconfig("end", foreground=color)
        self.alert_list.see("end")
        if bell:
            self.root.bell()

    # ------------------------------------------------------------ Anzeige Übersicht
    def _show_snapshot(self, s: Snapshot) -> None:
        values = {
            "CPU": (s.cpu_percent, f"{s.cpu_percent:5.1f} %   ({s.cpu_cores} Kerne)"),
            "RAM": (s.ram_percent, f"{s.ram_percent:5.1f} %   ({s.ram_used_gb:.1f} / {s.ram_total_gb:.1f} GB)"),
            "Festplatte": (s.disk_percent,
                           f"{s.disk_percent:5.1f} %   ({s.disk_used_gb:.0f} / {s.disk_total_gb:.0f} GB, {s.disk_path})"),
        }
        thresholds = self.monitor.config.thresholds()
        for name, (pct, text) in values.items():
            self.bars[name]["value"] = pct
            self.bars[name].configure(style=f"{self._color(pct, thresholds[name])}.Horizontal.TProgressbar")
            self.value_labels[name].config(text=text)
        self.info_label.config(text=f"Systemlaufzeit: {format_uptime(s.uptime_s)}    "
                                    f"Schwellen: " + ", ".join(f"{k} {v:.0f} %" for k, v in thresholds.items()))
        if s.processes is self._last_processes:     # Prozessliste unverändert -> Tabelle nicht neu aufbauen
            return
        self._last_processes = s.processes
        self.tree.delete(*self.tree.get_children())
        for p in s.processes:
            self.tree.insert("", "end", values=(p.pid, p.name, f"{p.cpu_percent:.1f}",
                                                f"{p.memory_percent:.1f}", f"{p.memory_mb:.0f}"))

    @staticmethod
    def _color(value: float, threshold: float) -> str:
        if value >= threshold:
            return "rot"
        if value >= threshold - 10:
            return "gelb"
        return "gruen"

    # ------------------------------------------------------------ Anzeige Laufwerke
    def _show_drives(self, drives: list[DriveInfo]) -> None:
        limit = self.monitor.config.disk_threshold
        self.drive_tree.delete(*self.drive_tree.get_children())
        for d in drives:
            tags = ("voll",) if d.percent >= limit else ("extern",) if d.external else ()
            self.drive_tree.insert("", "end", tags=tags, values=(
                d.mountpoint, d.kind, d.fstype, f"{d.used_gb:.1f} GB", f"{d.free_gb:.1f} GB",
                f"{d.total_gb:.1f} GB", f"{d.percent:.1f} %"))
        external = {d.mountpoint for d in drives if d.external}
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
        self.signal_bar.configure(style=("gruen" if sig >= 60 else "gelb" if sig >= 30 else "rot")
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
        self._update_traffic()

    def _update_traffic(self) -> None:
        counters = self.meter.read()                     # Zähler nur einmal pro Runde lesen
        names = self.meter.interfaces(counters)
        if names != self._nic_names:                     # Auswahlliste nur bei Änderung neu setzen
            self._nic_names = names
            self.nic_box["values"] = names
        nic = self.nic_var.get()
        sample = self.meter.sample(nic, counters) if nic else None
        if sample is None:
            self.down_label.config(text="↓ –")
            self.up_label.config(text="↑ –")
            self.total_label.config(text="Keine Netzwerkkarte gewählt." if not nic else f"'{nic}' nicht gefunden.")
            return
        self.down_label.config(text=f"↓ {format_rate(sample.down_bps)}")
        self.up_label.config(text=f"↑ {format_rate(sample.up_bps)}")
        self.total_label.config(text=f"Seit Programmstart: ↓ {format_bytes(sample.total_down)}   "
                                     f"↑ {format_bytes(sample.total_up)}")
        if self._current_tab() == TAB_NETWORK:           # Diagramm nur zeichnen, wenn sichtbar
            self._draw_graph()

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
            c.create_line(left, y, w - 5, y, fill="#eeeeee")
            c.create_text(left - 5, y, text=format_rate(peak * (4 - i) / 4), anchor="e",
                          fill=GREY, font=("Segoe UI", 8))
        c.create_text(left, h - 5, text=f"letzte {len(data)} Messungen", anchor="sw", fill=GREY, font=("Segoe UI", 8))
        c.create_text(w - 5, h - 5, text="↓ Download   ↑ Upload", anchor="se", fill=GREY, font=("Segoe UI", 8))
        if len(data) < 2:
            return
        step = (w - 5 - left) / (self.meter.history.maxlen - 1)
        x0 = w - 5 - step * (len(data) - 1)
        for idx, color in ((0, BLUE), (1, ORANGE)):
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
        SettingsDialog(self.root, self.monitor.config, self._apply_settings)

    def _apply_settings(self, new_cfg: Config) -> None:
        new_cfg.save(self.config_path)
        self.monitor.apply_config(new_cfg)
        log.info("Einstellungen geändert: %s", new_cfg)
        self.status.config(text="Einstellungen gespeichert")

    def quit(self) -> None:
        if self._job:
            self.root.after_cancel(self._job)
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
    )
    INT_FIELDS = {"alert_cooldown_s", "top_processes", "drive_refresh_s", "wlan_refresh_s", "bt_refresh_s"}

    def __init__(self, parent: tk.Tk, config: Config, on_save) -> None:
        super().__init__(parent)
        self.title("Einstellungen")
        self.resizable(False, False)
        self.transient(parent)
        self.config_obj = config
        self.on_save = on_save
        self.vars: dict[str, tk.StringVar] = {}

        for row, (key, label, lo, hi, step) in enumerate(self.FIELDS):
            ttk.Label(self, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=3)
            var = tk.StringVar(value=str(getattr(config, key)))
            ttk.Spinbox(self, from_=lo, to=hi, increment=step, textvariable=var, width=10).grid(
                row=row, column=1, padx=10, pady=3)
            self.vars[key] = var

        row = len(self.FIELDS)
        ttk.Label(self, text="Laufwerk/Pfad (leer = System)").grid(row=row, column=0, sticky="w", padx=10, pady=3)
        self.disk_var = tk.StringVar(value=config.disk_path)
        ttk.Entry(self, textvariable=self.disk_var, width=12).grid(row=row, column=1, padx=10, pady=3)
        self.upd_var = tk.BooleanVar(value=config.check_updates_on_start)
        ttk.Checkbutton(self, text="Sofort beim Start nach Updates suchen (sonst beim Öffnen des Tabs)",
                        variable=self.upd_var).grid(
            row=row + 1, column=0, columnspan=2, sticky="w", padx=10, pady=3)

        btns = ttk.Frame(self)
        btns.grid(row=row + 2, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text="Speichern", command=self._save).pack(side="left", padx=5)
        ttk.Button(btns, text="Abbrechen", command=self.destroy).pack(side="left", padx=5)

        self.grab_set()   # Dialog ist modal

    def _save(self) -> None:
        try:
            changes = {}
            for key, *_ in self.FIELDS:
                value = float(self.vars[key].get().replace(",", "."))
                changes[key] = int(value) if key in self.INT_FIELDS else value
            changes["disk_path"] = self.disk_var.get().strip()
            changes["check_updates_on_start"] = bool(self.upd_var.get())
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
