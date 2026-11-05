"""Software-Updates über winget (Windows-Paket-Manager)."""
from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass, field

from .winutil import IS_WINDOWS, NotSupportedError, run_command

log = logging.getLogger(__name__)

AGREEMENTS = ["--accept-source-agreements", "--accept-package-agreements"]
_SAFE_ID = re.compile(r"^[\w.\-+]+$")      # winget-IDs: Buchstaben, Ziffern, . - _ +


@dataclass(frozen=True)
class UpdateInfo:
    name: str
    package_id: str
    installed: str
    available: str
    source: str


@dataclass
class UpdateResult:
    updates: list[UpdateInfo] = field(default_factory=list)
    message: str = ""


def _clean_lines(text: str) -> list[str]:
    # winget schreibt Fortschrittsanzeigen mit '\r' -> nur der Teil nach dem letzten '\r' zählt
    return [line.split("\r")[-1].rstrip() for line in text.replace("\r\n", "\n").split("\n")]


def _column_starts(header: str) -> list[int]:
    return [i for i, ch in enumerate(header) if ch != " " and (i == 0 or header[i - 1] == " ")]


def parse_winget_upgrade(text: str) -> list[UpdateInfo]:
    """Wertet die Tabelle von 'winget upgrade' aus (Spalten über die Kopfzeile, sprachunabhängig)."""
    lines = _clean_lines(text)
    dash = next((i for i, ln in enumerate(lines) if re.fullmatch(r"-{10,}", ln.strip())), None)
    if dash is None:
        return []
    header = next((lines[j] for j in range(dash - 1, -1, -1) if lines[j].strip()), "")
    starts = _column_starts(header)
    if len(starts) < 4:
        return []
    bounds = starts + [10_000]
    result: list[UpdateInfo] = []
    for line in lines[dash + 1:]:
        if not line.strip():
            break                                   # Tabellenende (danach ggf. weitere Tabellen)
        cols = [line[bounds[k]:bounds[k + 1]].strip() for k in range(len(starts))]
        cols += [""] * (5 - len(cols))
        name, pid, installed, available, source = cols[:5]
        if not pid or " " in pid or not installed or not available:
            continue                                # z. B. Zusammenfassung "3 Aktualisierungen verfügbar."
        result.append(UpdateInfo(name, pid, installed, available, source))
    return result


def list_updates() -> UpdateResult:
    if not IS_WINDOWS:
        return UpdateResult(message="winget gibt es nur unter Windows.")
    try:
        res = run_command(["winget", "upgrade", "--accept-source-agreements"], timeout=180)
    except NotSupportedError:
        return UpdateResult(message="winget wurde nicht gefunden (App-Installer aus dem Microsoft Store nötig).")
    except subprocess.TimeoutExpired:
        return UpdateResult(message="winget hat nicht innerhalb von 3 Minuten geantwortet.")
    except Exception as exc:
        return UpdateResult(message=f"winget fehlgeschlagen: {exc}")
    updates = parse_winget_upgrade(res.output)
    if updates:
        return UpdateResult(updates, f"{len(updates)} Update(s) verfügbar.")
    last = next((ln.strip() for ln in reversed(_clean_lines(res.output)) if ln.strip()), "")
    return UpdateResult(message=last or "Keine Updates gefunden.")


def build_upgrade_command(package_ids: list[str] | None) -> str:
    """Befehlszeile für cmd.exe. None = alle Pakete aktualisieren."""
    if package_ids is None:
        cmds = ["winget upgrade --all " + " ".join(AGREEMENTS)]
    else:
        bad = [p for p in package_ids if not _SAFE_ID.match(p)]
        if bad:
            raise ValueError(f"Ungültige Paket-ID: {', '.join(bad)}")
        cmds = [f"winget upgrade --id {p} -e " + " ".join(AGREEMENTS) for p in package_ids]
    return " & ".join(cmds) + " & echo. & echo Fertig. & pause"


def start_upgrade(package_ids: list[str] | None) -> None:
    """Startet die Aktualisierung in einem eigenen Konsolenfenster, damit der Fortschritt sichtbar ist.
    Manche Installer fragen per Benutzerkontensteuerung (UAC) nach Admin-Rechten."""
    if not IS_WINDOWS:
        raise NotSupportedError("winget gibt es nur unter Windows.")
    command = build_upgrade_command(package_ids)
    log.info("Starte Update: %s", command)
    subprocess.Popen(f'cmd.exe /c "{command}"', creationflags=subprocess.CREATE_NEW_CONSOLE)
