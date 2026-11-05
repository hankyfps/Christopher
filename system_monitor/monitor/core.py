"""Gemeinsamer Ablauf eines Messzyklus – wird von GUI und Terminal-Modus genutzt."""
from __future__ import annotations

import logging
import time
from pathlib import Path

from .alerts import Alert, AlertManager, Level
from .collector import Snapshot, SystemCollector
from .config import Config
from .storage import CsvWriter

log = logging.getLogger("monitor")


class Monitor:
    def __init__(self, config: Config, log_dir: Path) -> None:
        self.config = config
        self.collector = SystemCollector(config.effective_disk_path, config.top_processes,
                                         config.process_interval_s)
        self.alerts = AlertManager(config.thresholds(), config.alert_cooldown_s, config.hysteresis)
        self.csv = CsvWriter(log_dir / "messwerte.csv", config.csv_flush_s) if config.csv_logging else None
        self.last_duration_s = 0.0          # Dauer des letzten Messzyklus (Diagnose)
        self._slow_warned_at = float("-inf")

    def apply_config(self, config: Config) -> None:
        """Geänderte Einstellungen ohne Neustart übernehmen."""
        self.config = config
        self.collector.disk_path = config.effective_disk_path
        self.collector.top_n = config.top_processes
        self.collector.process_interval_s = config.process_interval_s
        self.collector.invalidate_processes()      # neue Einstellungen sofort bei der nächsten Messung
        if self.csv:
            self.csv.flush_s = config.csv_flush_s
        self.alerts.update_settings(config.thresholds(), config.alert_cooldown_s, config.hysteresis)

    def step(self, force_processes: bool = False, skip_processes: bool = False) -> tuple[Snapshot, list[Alert]]:
        """Ein Zyklus: messen -> Grenzwerte prüfen -> protokollieren.
        skip_processes=True spart den teuren Prozess-Scan; Grenzwertprüfung und CSV laufen trotzdem."""
        t0 = time.perf_counter()
        snap = self.collector.snapshot(force_processes, skip_processes)
        new_alerts = self.alerts.check(snap.metrics(), snap.timestamp)
        for a in new_alerts:
            (log.warning if a.level is Level.WARNUNG else log.info)(a.message())
        if self.csv:
            try:
                self.csv.write(snap)
            except OSError as exc:   # z. B. Datei in Excel geöffnet und gesperrt
                log.error("CSV konnte nicht geschrieben werden: %s", exc)
        self.last_duration_s = time.perf_counter() - t0
        # Diagnose: dauert eine Messung ungewöhnlich lange, höchstens einmal pro 10 Minuten ins Log
        if self.last_duration_s > 1.0 and time.monotonic() - self._slow_warned_at > 600:
            self._slow_warned_at = time.monotonic()
            log.warning("Messzyklus dauerte %.1f s (Prozessliste: %d Prozesse geprüft)",
                        self.last_duration_s, len(snap.processes))
        return snap, new_alerts

    def close(self) -> None:
        """Gepufferte CSV-Zeilen schreiben (beim Beenden aufrufen)."""
        if self.csv:
            try:
                self.csv.flush()
            except OSError as exc:
                log.error("CSV konnte nicht geschrieben werden: %s", exc)
