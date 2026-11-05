"""Konfiguration laden, prüfen und speichern (config.json)."""
from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass, fields
from pathlib import Path

from .overlay_logic import OVERLAY_STYLES, POSITIONS, parse_hotkey

log = logging.getLogger(__name__)


def default_disk_path() -> str:
    """Wurzel des aktuellen Laufwerks: unter Windows z. B. 'C:\\', unter Linux '/'."""
    return os.path.abspath(os.sep)


@dataclass
class Config:
    interval_s: float = 2.0          # Messintervall in Sekunden
    cpu_threshold: float = 85.0      # Warnschwelle CPU in %
    ram_threshold: float = 85.0      # Warnschwelle Arbeitsspeicher in %
    disk_threshold: float = 90.0     # Warnschwelle Festplatte in %
    hysteresis: float = 5.0          # Entwarnung erst unter (Schwelle - Hysterese)
    disk_path: str = ""              # leer = Systemlaufwerk automatisch
    alert_cooldown_s: int = 60       # Mindestabstand zwischen gleichen Warnungen
    top_processes: int = 10          # Anzahl angezeigter Prozesse
    process_interval_s: float = 30.0  # Prozessliste neu erstellen alle n s (teuerster Teil, nur wenn sichtbar)
    csv_logging: bool = True         # Messwerte zusätzlich in CSV schreiben
    csv_flush_s: int = 30            # CSV gebündelt alle n s schreiben (0 = sofort)
    log_dir: str = "logs"            # Ordner für Log- und CSV-Dateien
    net_interface: str = ""          # Netzwerkkarte für Traffic; leer = WLAN automatisch
    drive_refresh_s: int = 10        # Laufwerksliste neu einlesen alle n s
    wlan_refresh_s: int = 15         # WLAN-Status neu abfragen alle n s
    bt_refresh_s: int = 60           # Bluetooth neu abfragen alle n s (nur bei offenem Tab)
    check_updates_on_start: bool = False  # winget sofort beim Start (sonst beim 1. Öffnen des Tabs)
    overlay_enabled: bool = False    # Overlay beim Start anzeigen
    overlay_style: str = "bar"       # bar = Leiste, tile = Mini-Kachel, numbers = nur Zahlen
    overlay_position: str = "top-center"   # top-/bottom- + left/center/right
    overlay_alpha: float = 0.7       # Deckkraft des Overlays (0,2 = fast durchsichtig ... 1 = deckend)
    overlay_click_through: bool = True     # Mausklicks gehen durch das Overlay hindurch
    overlay_hotkey: str = "ctrl+alt+o"     # globales Tastenkürzel zum Ein-/Ausschalten (wirkt nach Neustart)
    overlay_hide_main: bool = True   # Hauptfenster verstecken, solange das Overlay an ist

    # ------------------------------------------------------------------
    def validate(self) -> None:
        """Wirft ValueError, wenn ein Wert außerhalb des erlaubten Bereichs liegt."""
        for name in ("cpu_threshold", "ram_threshold", "disk_threshold"):
            value = getattr(self, name)
            if not 1 <= value <= 100:
                raise ValueError(f"{name} muss zwischen 1 und 100 liegen (ist {value})")
        if not 0.5 <= self.interval_s <= 3600:
            raise ValueError(f"interval_s muss zwischen 0,5 und 3600 liegen (ist {self.interval_s})")
        if not 0 <= self.hysteresis < 50:
            raise ValueError(f"hysteresis muss zwischen 0 und 49 liegen (ist {self.hysteresis})")
        if self.alert_cooldown_s < 0:
            raise ValueError("alert_cooldown_s darf nicht negativ sein")
        if not 1 <= self.top_processes <= 50:
            raise ValueError("top_processes muss zwischen 1 und 50 liegen")
        if not 1 <= self.process_interval_s <= 3600:
            raise ValueError("process_interval_s muss zwischen 1 und 3600 liegen")
        if not 0 <= self.csv_flush_s <= 3600:
            raise ValueError("csv_flush_s muss zwischen 0 und 3600 liegen")
        if self.overlay_style not in OVERLAY_STYLES:
            raise ValueError(f"overlay_style muss eines von {', '.join(OVERLAY_STYLES)} sein (ist {self.overlay_style!r})")
        if self.overlay_position not in POSITIONS:
            raise ValueError(f"overlay_position muss eines von {', '.join(POSITIONS)} sein (ist {self.overlay_position!r})")
        if not 0.2 <= self.overlay_alpha <= 1.0:
            raise ValueError(f"overlay_alpha muss zwischen 0,2 und 1 liegen (ist {self.overlay_alpha})")
        parse_hotkey(self.overlay_hotkey)               # wirft ValueError bei ungültigem Kürzel
        for name in ("drive_refresh_s", "wlan_refresh_s", "bt_refresh_s"):
            if not 2 <= getattr(self, name) <= 3600:
                raise ValueError(f"{name} muss zwischen 2 und 3600 liegen")

    @property
    def effective_disk_path(self) -> str:
        return self.disk_path or default_disk_path()

    def thresholds(self) -> dict[str, float]:
        return {
            "CPU": self.cpu_threshold,
            "RAM": self.ram_threshold,
            "Festplatte": self.disk_threshold,
        }

    # ------------------------------------------------------------------
    @classmethod
    def load(cls, path: Path) -> "Config":
        """Lädt die Konfiguration. Fehlt die Datei, wird sie mit Standardwerten angelegt.
        Ist sie defekt oder ungültig, werden Standardwerte verwendet (Datei bleibt unverändert)."""
        if not path.exists():
            cfg = cls()
            cfg.save(path)
            log.info("Keine Konfiguration gefunden – Standardwerte gespeichert in %s", path)
            return cfg
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            known = {f.name for f in fields(cls)}
            unknown = set(data) - known
            if unknown:
                log.warning("Unbekannte Einträge in %s ignoriert: %s", path, ", ".join(sorted(unknown)))
            cfg = cls(**{k: v for k, v in data.items() if k in known})
            cfg.validate()
            return cfg
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            log.error("Konfiguration %s ungültig (%s) – verwende Standardwerte", path, exc)
            return cls()

    def save(self, path: Path) -> None:
        self.validate()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=4, ensure_ascii=False), encoding="utf-8")
