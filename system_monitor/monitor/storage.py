"""Protokollierung: Logdatei (Warnungen, Fehler) und CSV-Datei (Messwerte)."""
from __future__ import annotations

import csv
import logging
import threading
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .collector import Snapshot

CSV_HEADER = ["Zeitpunkt", "CPU_%", "RAM_%", "RAM_belegt_GB", "Festplatte_%", "Festplatte_belegt_GB"]


def setup_logging(log_dir: Path, console: bool = False) -> None:
    """Logdatei monitor.log, max. 1 MB, 3 Sicherungen (monitor.log.1 ...)."""
    log_dir.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    for h in root.handlers[:]:          # alte Handler sauber schließen (Datei freigeben)
        h.close()
        root.removeHandler(h)
    fmt = logging.Formatter("%(asctime)s  %(levelname)-8s %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")
    fh = RotatingFileHandler(log_dir / "monitor.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(fh)
    if console:
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        ch.setFormatter(fmt)
        root.addHandler(ch)


def _de(value: float) -> str:
    """Zahl mit Dezimalkomma, damit Excel (deutsch) sie direkt als Zahl erkennt."""
    return f"{value:.1f}".replace(".", ",")


class CsvWriter:
    """Sammelt Messungen und schreibt sie gebündelt in messwerte.csv (Trennzeichen ';').
    Gebündeltes Schreiben schont Festplatte und Cloud-Sync (z. B. OneDrive), der sonst
    bei jeder Messung die Datei neu hochladen würde."""

    def __init__(self, path: Path, flush_s: float = 30.0, clock=time.monotonic) -> None:
        self.path = path
        self.flush_s = flush_s
        self._clock = clock
        self._rows: list[list[str]] = []
        self._last_flush = clock()
        self._lock = threading.Lock()      # Mess-Thread und Programmende können gleichzeitig schreiben
        path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, s: Snapshot) -> None:
        with self._lock:
            self._rows.append([
                s.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                _de(s.cpu_percent), _de(s.ram_percent), _de(s.ram_used_gb),
                _de(s.disk_percent), _de(s.disk_used_gb),
            ])
        if self.flush_s <= 0 or self._clock() - self._last_flush >= self.flush_s or len(self._rows) >= 500:
            self.flush()

    def flush(self) -> None:
        with self._lock:
            self._flush_locked()

    def _flush_locked(self) -> None:
        if not self._rows:
            return
        new_file = not self.path.exists() or self.path.stat().st_size == 0
        # utf-8-sig: Excel erkennt Umlaute korrekt
        with self.path.open("a", newline="", encoding="utf-8-sig" if new_file else "utf-8") as f:
            w = csv.writer(f, delimiter=";")
            if new_file:
                w.writerow(CSV_HEADER)
            w.writerows(self._rows)
        self._rows.clear()
        self._last_flush = self._clock()
