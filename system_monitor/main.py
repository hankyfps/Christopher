"""System-Monitor – Einstiegspunkt.

Aufruf:
    python main.py            Fenster (GUI)
    python main.py --nogui    Terminal-Modus
    python main.py --once     eine Messung ausgeben und beenden
    python main.py --updates  verfügbare Updates (winget) anzeigen
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from monitor import __version__
from monitor.config import Config
from monitor.core import Monitor
from monitor.storage import setup_logging

BASE_DIR = Path(__file__).resolve().parent


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Überwacht CPU, Arbeitsspeicher und Festplatte.")
    p.add_argument("--nogui", action="store_true", help="im Terminal statt im Fenster laufen")
    p.add_argument("--once", action="store_true", help="eine Messung ausgeben und beenden")
    p.add_argument("--updates", action="store_true", help="verfügbare Updates (winget) anzeigen und beenden")
    p.add_argument("--config", type=Path, default=BASE_DIR / "config.json", help="Pfad zur Konfigurationsdatei")
    p.add_argument("--version", action="version", version=f"System-Monitor {__version__}")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    # Umleitung in Datei/Pipe: nicht darstellbare Zeichen (z. B. ↓ ↑) ersetzen statt abzustürzen
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    use_gui = not (args.nogui or args.once or args.updates)

    # Logging zuerst mit Standardordner, damit Fehler beim Laden der Konfiguration protokolliert werden
    setup_logging(BASE_DIR / "logs", console=True)
    config = Config.load(args.config)
    log_dir = Path(config.log_dir)
    if not log_dir.is_absolute():
        log_dir = BASE_DIR / log_dir
    setup_logging(log_dir, console=not use_gui)
    log = logging.getLogger("monitor")
    log.info("Programm gestartet (Version %s, Modus %s)", __version__, "GUI" if use_gui else "Terminal")

    monitor = Monitor(config, log_dir)

    if use_gui:
        try:
            from monitor.gui import run_gui
        except ImportError:     # tkinter nicht installiert (z. B. Linux ohne python3-tk)
            print("tkinter nicht verfügbar – starte im Terminal-Modus.", file=sys.stderr)
            use_gui = False
        else:
            run_gui(monitor, args.config)

    if not use_gui:
        from monitor.cli import run_cli
        try:
            run_cli(monitor, once=args.once, updates=args.updates)
        finally:
            monitor.close()                 # gepufferte CSV-Zeilen schreiben

    log.info("Programm beendet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
