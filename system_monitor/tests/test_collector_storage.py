from monitor.collector import SystemCollector, format_uptime
from monitor.config import Config, default_disk_path
from monitor.core import Monitor
from monitor.storage import CSV_HEADER, CsvWriter


def test_snapshot_werte_plausibel():
    s = SystemCollector(default_disk_path(), top_n=5).snapshot()
    for v in (s.cpu_percent, s.ram_percent, s.disk_percent):
        assert 0 <= v <= 100
    assert s.ram_total_gb > 0 and s.disk_total_gb > 0
    assert len(s.processes) <= 5
    assert set(s.metrics()) == {"CPU", "RAM", "Festplatte"}


def test_prozesse_sortiert():
    s = SystemCollector(default_disk_path(), top_n=20).snapshot()
    keys = [(p.cpu_percent, p.memory_percent) for p in s.processes]
    assert keys == sorted(keys, reverse=True)


def test_format_uptime():
    assert format_uptime(3 * 3600 + 5 * 60) == "03:05 h"
    assert format_uptime(2 * 86400 + 3600) == "2 T 01:00 h"


def test_csv_kopfzeile_nur_einmal(tmp_path):
    w = CsvWriter(tmp_path / "m.csv", flush_s=0)      # 0 = sofort schreiben
    snap = SystemCollector(default_disk_path(), 1).snapshot()
    w.write(snap)
    w.write(snap)
    lines = (tmp_path / "m.csv").read_text(encoding="utf-8-sig").splitlines()
    assert lines[0] == ";".join(CSV_HEADER)
    assert len(lines) == 3
    assert "," in lines[1].split(";")[1]       # Dezimalkomma


def test_monitor_step_mit_niedriger_schwelle_meldet(tmp_path):
    cfg = Config(cpu_threshold=1, ram_threshold=1, disk_threshold=1)
    mon = Monitor(cfg, tmp_path)
    _, alerts = mon.step()
    metrics = {a.metric for a in alerts}
    assert {"RAM", "Festplatte"} <= metrics          # RAM/Platte sind sicher > 1 %
    mon.close()                                      # Puffer schreiben
    assert (tmp_path / "messwerte.csv").exists()


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def test_csv_wird_gebuendelt_geschrieben(tmp_path):
    clock = FakeClock()
    w = CsvWriter(tmp_path / "m.csv", flush_s=30, clock=clock)
    snap = SystemCollector(default_disk_path(), 1).snapshot()
    w.write(snap)
    w.write(snap)
    assert not (tmp_path / "m.csv").exists()          # noch im Puffer
    clock.t = 30
    w.write(snap)                                      # Intervall erreicht -> alles schreiben
    lines = (tmp_path / "m.csv").read_text(encoding="utf-8-sig").splitlines()
    assert len(lines) == 4                             # Kopf + 3 Zeilen


def test_prozessliste_nur_im_intervall():
    clock = FakeClock()
    c = SystemCollector(default_disk_path(), 5, process_interval_s=5, clock=clock)
    calls = []
    orig = c._top_processes
    c._top_processes = lambda: calls.append(1) or orig()
    c.snapshot()
    clock.t = 2
    s2 = c.snapshot()
    assert len(calls) == 1 and s2.processes is c._processes   # alte Liste wiederverwendet
    clock.t = 5
    c.snapshot()
    assert len(calls) == 2
    c.snapshot(force_processes=True)
    assert len(calls) == 3


def test_monitor_misst_dauer(tmp_path):
    mon = Monitor(Config(csv_logging=False), tmp_path)
    mon.step()
    assert 0 < mon.last_duration_s < 5


# ---------------------------------------------------------------- CPU-Auslastung (Fehler aus v2.1)
from collections import namedtuple  # noqa: E402

from monitor.collector import cpu_percent_between, cpu_totals  # noqa: E402


def test_cpu_berechnung():
    assert cpu_percent_between((100, 80), (200, 130)) == 50.0      # 100 s gesamt, 50 s Leerlauf
    assert cpu_percent_between((100, 80), (200, 180)) == 0.0
    assert cpu_percent_between((100, 80), (100, 80), previous=42.0) == 42.0   # kein Zeitabstand


def test_cpu_totals_wie_psutil():
    T = namedtuple("T", "user nice system idle iowait guest guest_nice")
    total, idle = cpu_totals(T(10, 0, 5, 80, 5, 2, 0))
    assert total == 100 and idle == 85                              # guest abgezogen, iowait = Leerlauf


def test_cpu_wird_auch_in_neuen_threads_gemessen():
    """Regression: Jede Messung läuft in einem neuen Thread (wie im Fenster). psutil.cpu_percent()
    lieferte dort immer 0 %, weil es sich den Vergleichswert pro Thread merkt."""
    import subprocess
    import sys
    import threading
    import time
    busy = subprocess.Popen([sys.executable, "-c", "while True: pass"])
    try:
        c = SystemCollector(default_disk_path(), 1)
        keep_alive = []                       # laufende Threads -> jeder neue bekommt eine neue ID
        stop = threading.Event()
        values = []
        for _ in range(3):
            time.sleep(0.6)
            t = threading.Thread(target=lambda: (values.append(c.snapshot().cpu_percent), stop.wait()))
            t.start()
            keep_alive.append(t)
            while len(values) < len(keep_alive):
                time.sleep(0.01)
        stop.set()
        assert len({t.ident for t in keep_alive}) == 3
        assert all(v > 5 for v in values), values      # ein voll ausgelasteter Kern ist deutlich > 5 %
    finally:
        busy.kill()
