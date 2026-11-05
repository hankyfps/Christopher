"""TEMPORÄRE Diagnose: Warum dauert die Prozessliste so lange? (gehört nicht zum Programm)

Misst ohne Fenster:
  1. Anzahl Prozesse und Dauer von process_iter() je abgefragtem Wert
  2. die langsamsten einzelnen Prozesse (Name) beim Lesen von memory_info
  3. Dauer von net_io_counters / disk_partitions / cpu_times (alles, was die Oberfläche im Hauptthread nutzt)
  4. dasselbe nochmal, während im Hintergrund die Prozessliste läuft (zeigt Sperr-Effekte zwischen Threads)

Aufruf:  py tools\\prozess_diagnose.py
"""
from __future__ import annotations

import json
import platform
import statistics
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import psutil

ROOT = Path(__file__).resolve().parent.parent
OUT: dict = {}


def ms(fn, n=1) -> list[float]:
    vals = []
    for _ in range(n):
        t0 = time.perf_counter()
        fn()
        vals.append((time.perf_counter() - t0) * 1000)
    return vals


def line(label: str, vals: list[float]) -> None:
    med, mx = statistics.median(vals), max(vals)
    print(f"  {label:58s} n={len(vals):3d}  Median {med:9.1f} ms   Max {mx:9.1f} ms")
    OUT[label] = {"n": len(vals), "median_ms": round(med, 2), "max_ms": round(mx, 2)}


def iter_attrs(attrs):
    def run():
        for p in psutil.process_iter(attrs, ad_value=None):
            p.info
    return run


def section_processes() -> None:
    print("\n[1] process_iter() je Wert (alle Prozesse, ad_value=None)")
    n = len(psutil.pids())
    print(f"  Prozesse laufend: {n}")
    OUT["prozesse"] = n
    list(psutil.process_iter(["cpu_percent"]))          # Startwerte für cpu_percent setzen
    for label, attrs in (("nur pid", ["pid"]), ("name", ["pid", "name"]), ("cpu_percent", ["pid", "cpu_percent"]),
                         ("cpu_times", ["pid", "cpu_times"]), ("memory_info", ["pid", "memory_info"]),
                         ("so wie im Programm (pid,name,cpu_percent,memory_info)",
                          ["pid", "name", "cpu_percent", "memory_info"])):
        line(label, ms(iter_attrs(attrs), 3))
    denied = {"memory_info": 0, "cpu_times": 0, "name": 0}
    for p in psutil.process_iter(["name", "cpu_times", "memory_info"], ad_value=None):
        for k in denied:
            if p.info.get(k) is None:
                denied[k] += 1
    print(f"  Prozesse ohne Zugriff (None): {denied}")
    OUT["ohne_zugriff"] = denied


def section_slowest() -> None:
    print("\n[2] langsamste Prozesse beim Lesen von memory_info (einzeln)")
    rows = []
    for p in psutil.process_iter(["pid", "name"], ad_value=None):
        t0 = time.perf_counter()
        try:
            p.memory_info()
            ok = "ok"
        except psutil.Error as exc:
            ok = type(exc).__name__
        rows.append(((time.perf_counter() - t0) * 1000, p.info["name"], ok))
    rows.sort(reverse=True)
    for t, name, ok in rows[:8]:
        print(f"  {t:8.1f} ms  {name}  ({ok})")
    total = sum(r[0] for r in rows)
    print(f"  Summe aller Einzelabfragen: {total:.0f} ms bei {len(rows)} Prozessen")
    OUT["langsamste"] = [{"ms": round(t, 1), "name": n, "status": o} for t, n, o in rows[:8]]


def section_main_thread_calls(prefix: str) -> None:
    line(f"{prefix}net_io_counters(pernic=True)", ms(lambda: psutil.net_io_counters(pernic=True), 20))
    line(f"{prefix}cpu_times()", ms(psutil.cpu_times, 20))
    line(f"{prefix}virtual_memory()", ms(psutil.virtual_memory, 20))
    line(f"{prefix}disk_usage(Systemlaufwerk)", ms(lambda: psutil.disk_usage(Path.cwd().anchor or "/"), 20))
    line(f"{prefix}disk_partitions()", ms(lambda: psutil.disk_partitions(all=False), 5))


def section_contention() -> None:
    print("\n[3] Aufrufe, die die Oberfläche im Hauptthread macht – Prozessliste ruht")
    section_main_thread_calls("ruhig: ")
    print("\n[4] dieselben Aufrufe, während im Hintergrund die Prozessliste läuft")
    done = threading.Event()

    def bg():
        for _ in range(2):
            for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"], ad_value=None):
                p.info
        done.set()

    threading.Thread(target=bg, daemon=True).start()
    time.sleep(0.2)
    section_main_thread_calls("parallel: ")
    print(f"  (Hintergrund fertig: {done.is_set()})")
    done.wait(60)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    sys.setswitchinterval(0.001)
    print(f"{platform.platform()} | Python {platform.python_version()} | psutil {psutil.__version__} | "
          f"{psutil.cpu_count()} CPUs")
    section_processes()
    section_slowest()
    section_contention()
    out_dir = ROOT / "messungen"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"prozess_diagnose_{datetime.now():%Y%m%d-%H%M%S}.json"
    out.write_text(json.dumps(OUT, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nErgebnis gespeichert: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
