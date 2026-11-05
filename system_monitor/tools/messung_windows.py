"""TEMPORÄRES Messskript für den System-Monitor (gehört nicht zum Programm).

Startet die echte Oberfläche (MonitorApp) und misst:
  a) Verspätung eines 20-ms-after()-Timers (zeigt, ob das Fenster ruckelt)
  b) Dauer von Monitor.step() mit und ohne Prozessliste
  c) Dauer der GUI-Updates, Tab-Wechsel und Fenster-Größenänderung
  d) CPU-Last und RAM des eigenen Prozesses (Fenster sichtbar / minimiert)
Dazu ein paar kleine Einzeltests (Thread-Start, Meldungsliste, root.bell()).

Aufruf (im Projektordner):
    py tools\\messung_windows.py --tab uebersicht --label vorher
    py tools\\messung_windows.py --tab netzwerk   --label vorher
Vergleich zweier Läufe:
    py tools\\messung_windows.py --vergleich messungen\\A.json messungen\\B.json

Während der Messung: Maus und Tastatur nicht benutzen, keine anderen großen Programme offen.
Das Skript schreibt nichts in logs\\ und ändert config.json nicht (nutzt einen Temp-Ordner).
"""
from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import tempfile
import threading
import time
import tkinter as tk
from collections import defaultdict
from dataclasses import replace
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import psutil  # noqa: E402

from monitor import __version__, gui  # noqa: E402
from monitor.collector import SystemCollector  # noqa: E402
from monitor.config import Config  # noqa: E402
from monitor.core import Monitor  # noqa: E402
from monitor.tasks import BackgroundRunner  # noqa: E402

TABS = {"uebersicht": gui.TAB_OVERVIEW, "laufwerke": gui.TAB_DRIVES, "netzwerk": gui.TAB_NETWORK}

# ---------------------------------------------------------------- Aufzeichnung
PHASE: str | None = None                          # aktuelle Messphase (None = nichts aufzeichnen)
TIMES: dict[tuple[str, str], list[float]] = defaultdict(list)   # (Phase, Name) -> Millisekunden
COUNT: dict[tuple[str, str], int] = defaultdict(int)
NOTES: list[str] = []


def record(name: str, ms: float) -> None:
    if PHASE and not PHASE.startswith("cpu_"):       # in den CPU-Phasen nichts aufzeichnen (Messfehler vermeiden)
        TIMES[(PHASE, name)].append(ms)


def patch(cls, name: str) -> None:
    """Methode so umhüllen, dass ihre Laufzeit aufgezeichnet wird (inklusive aufgerufener Methoden)."""
    orig = getattr(cls, name, None)
    if orig is None:
        if name in ("_on_tab_changed", "_on_view_changed"):      # je nach Oberfläche gibt es nur eine davon
            return
        NOTES.append(f"Methode {cls.__name__}.{name} gibt es nicht – übersprungen")
        return

    def wrapper(*a, **k):
        t0 = time.perf_counter()
        try:
            return orig(*a, **k)
        finally:
            record(name, (time.perf_counter() - t0) * 1000)

    wrapper.__name__ = name
    setattr(cls, name, wrapper)


def select_tab(app, idx: int) -> None:
    """Ansicht wechseln: Cyberpunk-Oberfläche (select_view) oder ältere Tabs (notebook)."""
    if hasattr(app, "select_view"):
        app.select_view(idx)
    else:
        app.notebook.select(idx)


def install_probes() -> None:
    for name in ("_tick", "_show_measurement", "_update_traffic", "_draw_graph", "_show_drives",
                 "_poll_background", "_on_tab_changed", "_on_view_changed"):
        patch(gui.MonitorApp, name)
    patch(SystemCollector, "_top_processes")

    orig_snap = gui.MonitorApp._show_snapshot

    def snap(self, s):                  # getrennt erfassen, ob die Prozesstabelle neu gebaut wird
        neu = s.processes is not getattr(self, "_last_processes", None)
        t0 = time.perf_counter()
        try:
            return orig_snap(self, s)
        finally:
            record("_show_snapshot[neue Prozessliste]" if neu else "_show_snapshot[unveraendert]",
                   (time.perf_counter() - t0) * 1000)

    gui.MonitorApp._show_snapshot = snap

    orig_step = Monitor.step

    def step(self, *args, **kwargs):
        before = self.collector._processes_at
        t0 = time.perf_counter()
        try:
            return orig_step(self, *args, **kwargs)
        finally:
            ms = (time.perf_counter() - t0) * 1000
            record("step[mit Prozessliste]" if self.collector._processes_at != before
                   else "step[ohne Prozessliste]", ms)

    Monitor.step = step

    orig_submit = BackgroundRunner.submit

    def submit(self, key, *a, **k):
        ok = orig_submit(self, key, *a, **k)
        if ok and PHASE:
            COUNT[(PHASE, "threads_gestartet")] += 1
            COUNT[(PHASE, f"threads_gestartet:{key}")] += 1
        return ok

    BackgroundRunner.submit = submit


# ---------------------------------------------------------------- Statistik
def stats(vals: list[float]) -> dict | None:
    if not vals:
        return None
    v = sorted(vals)

    def pct(p: float) -> float:
        return v[min(len(v) - 1, int(round(p / 100 * (len(v) - 1))))]

    return {"n": len(v), "median": round(statistics.median(v), 2), "mean": round(statistics.fmean(v), 2),
            "p95": round(pct(95), 2), "p99": round(pct(99), 2), "max": round(v[-1], 2)}


def rss_mb() -> float:
    return psutil.Process().memory_info().rss / 1024 ** 2


class CpuMeter:
    """CPU-Zeit des eigenen Prozesses (user+system) im Verhältnis zur verstrichenen Zeit."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.proc = psutil.Process()
        self.running = False
        self._after: str | None = None
        self.samples: list[float] = []

    def _cpu(self) -> float:
        t = self.proc.cpu_times()
        return t.user + t.system

    def begin(self) -> None:
        self.t0, self.c0 = time.perf_counter(), self._cpu()
        self.last = (self.t0, self.c0)
        self.samples = []
        self.running = True
        self._after = self.root.after(5000, self._sample)

    def _sample(self) -> None:           # alle 5 s ein Zwischenwert (Windows misst CPU-Zeit nur grob, ~16 ms)
        if not self.running:
            return
        now, cpu = time.perf_counter(), self._cpu()
        self.samples.append((cpu - self.last[1]) / (now - self.last[0]) * 100)
        self.last = (now, cpu)
        self._after = self.root.after(5000, self._sample)

    def end(self) -> dict:
        self.running = False
        if self._after:
            self.root.after_cancel(self._after)
            self._after = None
        wall, cpu = time.perf_counter() - self.t0, self._cpu() - self.c0
        pct_core = cpu / wall * 100
        return {"sekunden": round(wall, 1), "cpu_prozent_eines_kerns": round(pct_core, 2),
                "cpu_prozent_gesamt": round(pct_core / (psutil.cpu_count() or 1), 3),
                "max_5s_prozent_eines_kerns": round(max(self.samples), 2) if self.samples else None}


# ---------------------------------------------------------------- Einzeltests
def mikro_tests(cfg: Config, tmpdir: Path, n: int) -> None:
    """Ohne Fenster: Dauer von step() mit/ohne Prozessliste und Kosten eines Threads."""
    global PHASE
    PHASE = "mikro"
    mon = Monitor(replace(cfg, csv_logging=False), tmpdir)
    mon.step(True)
    mon.step(True)
    for _ in range(n):
        mon.step(False)
        time.sleep(0.3)
        mon.step(True)
        time.sleep(0.3)
    for _ in range(300):
        t0 = time.perf_counter()
        th = threading.Thread(target=lambda: None)
        th.start()
        th.join()
        record("thread_start_und_join", (time.perf_counter() - t0) * 1000)
    PHASE = None


def sync_tests(root: tk.Tk, app, tab_index: int, do_bell: bool) -> None:
    """Blockierende Tests im laufenden Fenster."""
    def safe(name, fn):
        try:
            fn()
        except Exception as exc:                       # Messskript soll nie am Test scheitern
            NOTES.append(f"Test {name} übersprungen: {type(exc).__name__}: {exc}")

    def meldungen():
        app.alert_list.delete(0, "end")
        for key, count in (("add_message[leere Liste, 200x]", 200), ("add_message[nach 5000 Eintraegen, 200x]", 200)):
            for i in range(count):
                t0 = time.perf_counter()
                app._add_message(f"{i} Testmeldung", "#000000")
                record(key, (time.perf_counter() - t0) * 1000)
            app.alert_list.insert("end", *[f"Füll {i}" for i in range(5000)])
        app.alert_list.delete(0, "end")

    def bell():
        for _ in range(3):
            t0 = time.perf_counter()
            root.bell()
            record("root.bell", (time.perf_counter() - t0) * 1000)
            time.sleep(0.4)

    def tabwechsel():
        for _ in range(10):
            for idx in (gui.TAB_OVERVIEW, gui.TAB_DRIVES, gui.TAB_NETWORK):
                t0 = time.perf_counter()
                select_tab(app, idx)
                root.update()
                record(f"tabwechsel_nach_{idx}", (time.perf_counter() - t0) * 1000)
        select_tab(app, tab_index)
        root.update()

    def resize():
        geo = root.geometry()
        min_w, min_h = root.minsize()
        for i in range(40):
            w, h = max(min_w, 760) + (i % 20) * 12, max(min_h, 580) + (i % 20) * 8
            t0 = time.perf_counter()
            root.geometry(f"{w}x{h}")
            root.update()
            record("fenstergroesse_aendern", (time.perf_counter() - t0) * 1000)
        root.geometry(geo.split("+")[0])
        root.update()

    global PHASE
    PHASE = "meldungen"
    safe("meldungen", meldungen)
    if do_bell:
        PHASE = "bell"
        safe("bell", bell)
    PHASE = "tabwechsel"
    safe("tabwechsel", tabwechsel)
    PHASE = "resize"
    safe("resize", resize)


# ---------------------------------------------------------------- Ablauf
def run_measurement(args) -> dict:
    global PHASE
    install_probes()
    cfg = Config.load(args.config)
    tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
    tmpdir = Path(tmp.name)
    cfg = replace(cfg, log_dir=str(tmpdir))
    if args.prozess_intervall is not None:
        cfg = replace(cfg, process_interval_s=args.prozess_intervall)
        NOTES.append(f"process_interval_s auf {args.prozess_intervall:g} s gesetzt (A/B-Test)")
    tab_index = TABS[args.tab]
    result: dict = {"cpu": {}, "rss_mb": {}}

    print(f"[1/3] Einzeltests ohne Fenster (~{int(args.mikro * 0.6 * 2) + 3} s) …", flush=True)
    mikro_tests(cfg, tmpdir, args.mikro)

    sys.setswitchinterval(0.001)                         # wie run_gui()
    root = tk.Tk()
    app = gui.MonitorApp(root, Monitor(cfg, tmpdir), tmpdir / "config.json")
    root.update()
    select_tab(app, tab_index)
    root.update()
    result["rss_mb"]["nach_start"] = round(rss_mb(), 1)
    cpu = CpuMeter(root)
    lag_state = {"last": None}

    def lag_tick() -> None:                              # 20-ms-Timer: wie spät kommt er wirklich?
        now = time.perf_counter()
        if lag_state["last"] is not None and PHASE == "idle":
            record("timer_verspaetung", (now - lag_state["last"]) * 1000 - 20)
        lag_state["last"] = now
        if PHASE in ("warmup", "idle"):
            root.after(20, lag_tick)

    def end_idle() -> None:
        result["rss_mb"]["nach_idle_phase"] = round(rss_mb(), 1)
        result["threads_am_ende"] = threading.active_count()

    def run_sync() -> None:
        print("[3/3] Blockierende Tests (Tab-Wechsel, Fenstergröße, Meldungen, bell) …", flush=True)
        sync_tests(root, app, tab_index, not args.ohne_bell)

    def cpu_end(name):
        def inner():
            result["cpu"][name] = cpu.end()
            if name == "minimiert":
                result["rss_mb"]["minimiert"] = round(rss_mb(), 1)
        return inner

    def minimize() -> None:
        root.iconify()

    def restore() -> None:
        root.deiconify()

    phases = [
        ("warmup", args.warmup, lambda: (print(f"[2/3] Fenster läuft, Tab '{args.tab}': Warmup {args.warmup} s …",
                                            flush=True), lag_tick()), None),
        ("idle", args.dauer, lambda: print(f"      Messung {args.dauer} s (nicht bedienen!) …", flush=True), end_idle),
        ("sync", 0, run_sync, None),
        ("cpu_sichtbar", args.cpu, lambda: (print(f"      CPU-Messung sichtbar {args.cpu} s …", flush=True),
                                            cpu.begin()), cpu_end("sichtbar")),
        ("cpu_minimiert", args.minimiert, lambda: (print(f"      CPU-Messung minimiert {args.minimiert} s …",
                                                         flush=True), minimize(), cpu.begin()),
         lambda: (cpu_end("minimiert")(), restore())),
    ]
    it = iter(phases)

    def next_phase() -> None:
        global PHASE
        try:
            name, dur, on_start, on_end = next(it)
        except StopIteration:
            PHASE = None
            app.quit()
            return
        PHASE = name
        on_start()

        def finish() -> None:
            if on_end:
                on_end()
            next_phase()
        root.after(int(dur * 1000), finish)

    root.after(200, next_phase)
    root.mainloop()
    PHASE = None
    tmp.cleanup()
    return result


def build_report(args, result: dict) -> dict:
    flat: dict[str, float] = {}
    st: dict[str, dict] = {}
    for (phase, name), vals in TIMES.items():
        s = stats(vals)
        if s:
            st[f"{phase}|{name}"] = s
            for k in ("median", "p95", "max", "n"):
                flat[f"{phase}|{name}|{k}"] = s[k]
    lag = TIMES.get(("idle", "timer_verspaetung"), [])
    lag_info = {"n": len(lag), "max_ms": round(max(lag), 1) if lag else None,
                "ueber_50ms": sum(1 for x in lag if x > 50), "ueber_100ms": sum(1 for x in lag if x > 100)}
    flat.update({f"timer|{k}": v for k, v in lag_info.items() if v is not None})
    for k, v in result["cpu"].items():
        for kk, vv in v.items():
            if vv is not None:
                flat[f"cpu_{k}|{kk}"] = vv
    for k, v in result["rss_mb"].items():
        flat[f"rss_mb|{k}"] = v
    threads_min = COUNT.get(("idle", "threads_gestartet"), 0) / max(args.dauer, 1) * 60
    flat["threads_pro_minute"] = round(threads_min, 1)
    return {
        "meta": {"zeit": datetime.now().isoformat(timespec="seconds"), "label": args.label, "tab": args.tab,
                 "version": __version__, "python": platform.python_version(), "tk": tk.TkVersion,
                 "psutil": psutil.__version__, "os": platform.platform(), "cpus": psutil.cpu_count(),
                 "dauer_s": args.dauer, "notizen": NOTES},
        "timer": lag_info, "stats": st, "cpu": result["cpu"], "rss_mb": result["rss_mb"],
        "threads": {k[1]: v for k, v in COUNT.items() if k[0] == "idle"}, "threads_pro_minute": round(threads_min, 1),
        "threads_am_ende": result.get("threads_am_ende"), "werte": flat,
    }


def _only(prefixes):
    return lambda name: name.startswith(prefixes)


def print_report(rep: dict) -> None:
    m = rep["meta"]
    print("\n" + "=" * 78)
    print(f"System-Monitor {m['version']} | Tab: {m['tab']} | Label: {m['label'] or '-'} | {m['zeit']}")
    print(f"{m['os']} | Python {m['python']} | Tk {m['tk']} | psutil {m['psutil']} | {m['cpus']} logische CPUs")
    print("=" * 78)
    t = rep["timer"]
    print(f"\n(a) 20-ms-Timer, Verspätung = Ist-Abstand minus 20 ms  ({t['n']} Messpunkte in {m['dauer_s']} s)")
    print(f"    Maximum: {t['max_ms']} ms | über 50 ms: {t['ueber_50ms']}x | über 100 ms: {t['ueber_100ms']}x")

    def block(title, prefix, names=None):
        rows = [(k.split("|", 1)[1], v) for k, v in rep["stats"].items() if k.startswith(prefix + "|")
                and (names is None or k.split("|", 1)[1] in names or k.split("|", 1)[1].startswith(tuple(names)))]
        if not rows:
            return
        print(f"\n{title}")
        print(f"    {'Name':42s}{'n':>6s}{'Median':>9s}{'P95':>9s}{'Max':>9s}   (ms)")
        for name, s in rows:
            print(f"    {name:42s}{s['n']:6d}{s['median']:9.2f}{s['p95']:9.2f}{s['max']:9.2f}")

    block("(b) step() ohne Fenster (Einzeltest, Hauptthread)", "mikro", {"step[mit Prozessliste]",
                                                                         "step[ohne Prozessliste]",
                                                                         "_top_processes"})
    block("(b) step() im laufenden Fenster (Hintergrund-Thread, Fenster arbeitet parallel)", "idle",
          {"step[mit Prozessliste]", "step[ohne Prozessliste]", "_top_processes"})
    block("(c) GUI-Updates im Hauptthread (inklusive Unteraufrufe)", "idle",
          {"_tick", "_show_measurement", "_show_snapshot[neue Prozessliste]", "_show_snapshot[unveraendert]",
           "_update_traffic", "_draw_graph", "_show_drives", "_poll_background"})
    block("(c) Tab-Wechsel Übersicht/Laufwerke/Netzwerk (select + update; Bluetooth/Updates bewusst nicht)",
          "tabwechsel", {"tabwechsel_nach_", "_draw_graph"})
    block("(c) Fenstergröße ändern (40 Schritte, inkl. Neuzeichnen; _draw_graph = Diagramm-Neuzeichnen)",
          "resize", {"fenstergroesse_aendern", "_draw_graph"})
    block("    Meldungsliste: Einfügen in leere Liste vs. nach 5000 Einträgen", "meldungen")
    block("    root.bell()", "bell")
    block("    Thread starten + beenden (Einzeltest)", "mikro", {"thread_start_und_join"})
    print(f"\n    Threads gestartet pro Minute (Idle-Phase): {rep['threads_pro_minute']}  {rep['threads']}")
    print("\n(d) Eigener Prozess")
    for k, v in rep["cpu"].items():
        print(f"    CPU {k:10s}: {v['cpu_prozent_eines_kerns']:6.2f} % eines Kerns = {v['cpu_prozent_gesamt']:.3f} % gesamt"
              f" | Max über 5 s: {v['max_5s_prozent_eines_kerns']} % ({v['sekunden']} s gemessen)")
    print(f"    RAM (Working Set): {rep['rss_mb']} MB | Threads am Ende: {rep['threads_am_ende']}")
    for n in m["notizen"]:
        print(f"    HINWEIS: {n}")
    print()


def compare(a_path: Path, b_path: Path) -> None:
    a, b = (json.loads(p.read_text(encoding="utf-8")) for p in (a_path, b_path))
    print(f"\nA = {a['meta']['label'] or a_path.name} ({a['meta']['tab']}, v{a['meta']['version']})")
    print(f"B = {b['meta']['label'] or b_path.name} ({b['meta']['tab']}, v{b['meta']['version']})\n")
    print(f"{'Messwert':62s}{'A':>10s}{'B':>10s}{'Änderung':>10s}")
    for key in sorted(set(a["werte"]) | set(b["werte"])):
        if key.endswith(("|p95", "|n")) and not key.startswith("timer"):
            continue
        va, vb = a["werte"].get(key), b["werte"].get(key)
        if va is None or vb is None:
            print(f"{key:62s}{str(va if va is not None else '-'):>10s}{str(vb if vb is not None else '-'):>10s}")
            continue
        delta = f"{(vb - va) / va * 100:+.0f}%" if va else "-"
        print(f"{key:62s}{va:10.2f}{vb:10.2f}{delta:>10s}")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    p = argparse.ArgumentParser(description="Messskript System-Monitor (temporär)")
    p.add_argument("--tab", choices=sorted(TABS), default="uebersicht")
    p.add_argument("--dauer", type=float, default=60, help="Messdauer Timer/GUI in s (mind. 60 empfohlen)")
    p.add_argument("--warmup", type=float, default=10)
    p.add_argument("--cpu", type=float, default=30, help="Dauer der CPU-Messung bei sichtbarem Fenster")
    p.add_argument("--minimiert", type=float, default=20, help="Dauer der CPU-Messung bei minimiertem Fenster")
    p.add_argument("--mikro", type=int, default=10, help="Durchläufe der Einzeltests")
    p.add_argument("--label", default="", help="z. B. vorher / nachher")
    p.add_argument("--ohne-bell", action="store_true", help="root.bell() nicht testen (kein Ton)")
    p.add_argument("--prozess-intervall", type=float, default=None,
                   help="process_interval_s überschreiben (z. B. 3600 = Prozessliste praktisch aus; für A/B-Vergleich)")
    p.add_argument("--config", type=Path, default=ROOT / "config.json")
    p.add_argument("--vergleich", nargs=2, type=Path, metavar=("A.json", "B.json"))
    args = p.parse_args()
    if args.vergleich:
        compare(*args.vergleich)
        return 0
    result = run_measurement(args)
    rep = build_report(args, result)
    print_report(rep)
    out_dir = ROOT / "messungen"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{(args.label or 'lauf')}_{args.tab}_{datetime.now():%Y%m%d-%H%M%S}.json"
    out.write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Ergebnis gespeichert: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
