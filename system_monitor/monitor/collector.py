"""Erfassung der Systemwerte mit psutil."""
from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime

import psutil

GB = 1024 ** 3
MB = 1024 ** 2


@dataclass(frozen=True)
class ProcessInfo:
    pid: int
    name: str
    cpu_percent: float      # bezogen auf die gesamte CPU (0–100 %)
    memory_percent: float
    memory_mb: float


@dataclass(frozen=True)
class Snapshot:
    """Eine Messung zu einem Zeitpunkt."""
    timestamp: datetime
    cpu_percent: float
    cpu_cores: int
    ram_percent: float
    ram_used_gb: float
    ram_total_gb: float
    disk_path: str
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    uptime_s: float
    processes: tuple[ProcessInfo, ...]

    def metrics(self) -> dict[str, float]:
        """Kennzahlen, die gegen die Schwellwerte geprüft werden."""
        return {
            "CPU": self.cpu_percent,
            "RAM": self.ram_percent,
            "Festplatte": self.disk_percent,
        }


class SystemCollector:
    """Misst die Systemwerte. Die Prozessliste ist der teuerste Teil (unter Windows müssen
    für geschützte Systemprozesse langsame Ersatzwege genutzt werden). Sie wird deshalb nur
    alle process_interval_s Sekunden neu erstellt, CPU/RAM/Festplatte dagegen bei jeder Messung."""

    def __init__(self, disk_path: str, top_n: int = 10, process_interval_s: float = 5.0,
                 clock=time.monotonic) -> None:
        self.disk_path = disk_path
        self.top_n = top_n
        self.process_interval_s = process_interval_s
        self._clock = clock
        self.cpu_cores = psutil.cpu_count(logical=True) or 1
        self._total_mem = psutil.virtual_memory().total
        self._processes: tuple[ProcessInfo, ...] = ()
        self._processes_at = float("-inf")
        # Startwert für die CPU-Berechnung (erste Messung danach liefert echte Werte)
        self._cpu_times = cpu_totals(psutil.cpu_times())
        self._cpu_percent = 0.0

    def invalidate_processes(self) -> None:
        """Prozessliste bei der nächsten Messung neu erstellen."""
        self._processes_at = float("-inf")

    def snapshot(self, force_processes: bool = False) -> Snapshot:
        now = self._clock()
        if force_processes or now - self._processes_at >= self.process_interval_s:
            self._processes = self._top_processes()
            self._processes_at = now
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage(self.disk_path)
        return Snapshot(
            timestamp=datetime.now(),
            cpu_percent=self._cpu_load(),
            cpu_cores=self.cpu_cores,
            ram_percent=mem.percent,
            ram_used_gb=(mem.total - mem.available) / GB,
            ram_total_gb=mem.total / GB,
            disk_path=self.disk_path,
            disk_percent=disk.percent,
            disk_used_gb=disk.used / GB,
            disk_total_gb=disk.total / GB,
            uptime_s=time.time() - psutil.boot_time(),
            processes=self._processes,
        )

    def _cpu_load(self) -> float:
        """CPU-Auslastung seit der letzten Messung.
        Bewusst NICHT psutil.cpu_percent(): Das merkt sich den Vergleichswert pro Thread.
        Da jede Messung in einem neuen Hintergrund-Thread läuft, käme dort immer 0 % heraus."""
        now = cpu_totals(psutil.cpu_times())
        self._cpu_percent = cpu_percent_between(self._cpu_times, now, self._cpu_percent)
        self._cpu_times = now
        return self._cpu_percent

    def _top_processes(self) -> tuple[ProcessInfo, ...]:
        procs: list[ProcessInfo] = []
        # process_iter merkt sich die Prozess-Objekte, dadurch liefert cpu_percent
        # ab der zweiten Messung echte Werte. Kein Zugriff (AccessDenied) -> None.
        # memory_percent wird selbst berechnet: psutil würde dafür memory_info ein zweites Mal abfragen
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"], ad_value=None):
            info = p.info
            if info["pid"] == 0:          # "System Idle Process" (Windows) überspringen
                continue
            mem_info = info.get("memory_info")
            procs.append(ProcessInfo(
                pid=info["pid"],
                name=info.get("name") or "?",
                cpu_percent=(info.get("cpu_percent") or 0.0) / self.cpu_cores,
                memory_percent=(mem_info.rss / self._total_mem * 100) if mem_info else 0.0,
                memory_mb=(mem_info.rss / MB) if mem_info else 0.0,
            ))
        procs.sort(key=lambda p: (p.cpu_percent, p.memory_percent), reverse=True)
        return tuple(procs[: self.top_n])


def cpu_totals(times) -> tuple[float, float]:
    """(Gesamtzeit, Leerlaufzeit) aus psutil.cpu_times() – so wie psutil selbst rechnet:
    guest-Zeiten sind unter Linux schon in user enthalten, iowait zählt als Leerlauf."""
    total = sum(times)
    total -= getattr(times, "guest", 0.0) + getattr(times, "guest_nice", 0.0)
    idle = times.idle + getattr(times, "iowait", 0.0)
    return total, idle


def cpu_percent_between(before: tuple[float, float], after: tuple[float, float],
                        previous: float = 0.0) -> float:
    """Auslastung in % zwischen zwei Messpunkten (Gesamt, Leerlauf)."""
    d_total = after[0] - before[0]
    d_idle = after[1] - before[1]
    if d_total <= 0:                 # zu kurzer Abstand -> letzten Wert behalten
        return previous
    return round(max(0.0, min(100.0, (d_total - d_idle) / d_total * 100)), 1)


def format_uptime(seconds: float) -> str:
    s = int(seconds)
    days, s = divmod(s, 86400)
    hours, s = divmod(s, 3600)
    minutes, _ = divmod(s, 60)
    return f"{days} T {hours:02d}:{minutes:02d} h" if days else f"{hours:02d}:{minutes:02d} h"
