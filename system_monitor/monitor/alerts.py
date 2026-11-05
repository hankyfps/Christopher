"""Grenzwertprüfung mit Cooldown (keine Warnungsflut) und Hysterese (kein Flattern)."""
from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable


class Level(Enum):
    WARNUNG = "WARNUNG"
    OK = "OK"


@dataclass(frozen=True)
class Alert:
    timestamp: datetime
    metric: str
    value: float
    threshold: float
    level: Level

    def message(self) -> str:
        zeit = self.timestamp.strftime("%H:%M:%S")
        if self.level is Level.WARNUNG:
            return (f"{zeit}  WARNUNG  {self.metric}: {self.value:.1f} % "
                    f"(Schwelle {self.threshold:.0f} %)")
        return f"{zeit}  OK       {self.metric}: wieder normal ({self.value:.1f} %)"


class AlertManager:
    def __init__(self, thresholds: dict[str, float], cooldown_s: float,
                 hysteresis: float = 5.0, clock: Callable[[], float] = time.monotonic) -> None:
        self.thresholds = dict(thresholds)
        self.cooldown_s = cooldown_s
        self.hysteresis = hysteresis
        self._clock = clock
        self._active: dict[str, float] = {}   # Kennzahl -> Zeitpunkt der letzten Warnung

    def update_settings(self, thresholds: dict[str, float], cooldown_s: float, hysteresis: float) -> None:
        self.thresholds = dict(thresholds)
        self.cooldown_s = cooldown_s
        self.hysteresis = hysteresis

    def is_active(self, metric: str) -> bool:
        return metric in self._active

    def check(self, metrics: dict[str, float], now: datetime | None = None) -> list[Alert]:
        """Prüft alle Kennzahlen und gibt neue Warnungen/Entwarnungen zurück."""
        now = now or datetime.now()
        t = self._clock()
        result: list[Alert] = []
        for name, value in metrics.items():
            limit = self.thresholds.get(name)
            if limit is None:
                continue
            if value >= limit:
                last = self._active.get(name)
                if last is None or t - last >= self.cooldown_s:
                    self._active[name] = t
                    result.append(Alert(now, name, value, limit, Level.WARNUNG))
            elif name in self._active and value < limit - self.hysteresis:
                del self._active[name]
                result.append(Alert(now, name, value, limit, Level.OK))
        return result
