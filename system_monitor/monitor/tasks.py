"""Langsame Abfragen (PowerShell, winget) im Hintergrund ausführen, damit das Fenster nicht einfriert.

tkinter darf nur aus dem Haupt-Thread bedient werden. Deshalb legt der Hintergrund-Thread
sein Ergebnis in eine Queue, und der Haupt-Thread holt es per poll() ab.
"""
from __future__ import annotations

import logging
import queue
import threading
from typing import Any, Callable

log = logging.getLogger(__name__)


class BackgroundRunner:
    def __init__(self) -> None:
        self._results: queue.Queue[tuple[str, Callable[[Any], None], Any]] = queue.Queue()
        self._running: set[str] = set()

    def is_running(self, key: str) -> bool:
        return key in self._running

    def submit(self, key: str, func: Callable[[], Any], on_done: Callable[[Any], None]) -> bool:
        """Startet func() in einem Thread. Läuft unter 'key' schon eine Abfrage, passiert nichts."""
        if key in self._running:
            return False
        self._running.add(key)

        def worker() -> None:
            try:
                result = func()
            except Exception as exc:          # Fehler als Ergebnis weiterreichen
                log.exception("Hintergrundaufgabe %s fehlgeschlagen", key)
                result = exc
            self._results.put((key, on_done, result))

        threading.Thread(target=worker, name=f"bg-{key}", daemon=True).start()
        return True

    def poll(self) -> int:
        """Im Haupt-Thread aufrufen: fertige Ergebnisse an ihre Callbacks übergeben."""
        count = 0
        while True:
            try:
                key, on_done, result = self._results.get_nowait()
            except queue.Empty:
                return count
            self._running.discard(key)
            on_done(result)
            count += 1
