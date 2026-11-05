"""Hilfsfunktionen zum Ausführen von Windows-Befehlen (netsh, PowerShell, winget)."""
from __future__ import annotations

import ctypes
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass

IS_WINDOWS = sys.platform == "win32"
# verhindert, dass bei jedem Aufruf kurz ein Konsolenfenster aufblitzt
_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


class NotSupportedError(RuntimeError):
    """Funktion ist auf diesem Betriebssystem nicht verfügbar."""


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    output: str


def decode_output(data: bytes) -> str:
    """Konsolenprogramme liefern je nach Tool UTF-8 oder die OEM-Codepage (z. B. cp850).
    Erst UTF-8 versuchen, sonst OEM-Codepage – so bleiben Umlaute korrekt."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        codepage = "cp850"
        if IS_WINDOWS:
            try:
                codepage = f"cp{ctypes.windll.kernel32.GetOEMCP()}"
            except (AttributeError, OSError):
                pass
        return data.decode(codepage, errors="replace")


def run_command(args: list[str], timeout: float = 30) -> CommandResult:
    """Startet ein Programm ohne Fenster und liefert Rückgabecode und Text-Ausgabe."""
    if shutil.which(args[0]) is None:
        raise NotSupportedError(f"'{args[0]}' wurde nicht gefunden")
    proc = subprocess.run(args, capture_output=True, timeout=timeout, creationflags=_NO_WINDOW)
    return CommandResult(proc.returncode, decode_output(proc.stdout + proc.stderr))


def run_powershell_json(script: str, timeout: float = 30):
    """Führt ein PowerShell-Skript aus, das JSON ausgibt, und liefert das Python-Objekt (oder None)."""
    if not IS_WINDOWS:
        raise NotSupportedError("nur unter Windows verfügbar")
    full = "[Console]::OutputEncoding = [Text.Encoding]::UTF8; $ErrorActionPreference = 'SilentlyContinue'; " + script
    res = run_command(["powershell", "-NoProfile", "-NonInteractive", "-Command", full], timeout)
    text = res.output.strip()
    if not text:
        return None
    # nur den JSON-Teil auswerten (falls PowerShell zusätzliche Zeilen ausgibt)
    start = min((i for i in (text.find("{"), text.find("[")) if i >= 0), default=-1)
    if start < 0:
        return None
    return json.loads(text[start:])


def as_list(value) -> list:
    """ConvertTo-Json liefert bei genau einem Element ein Objekt statt einer Liste."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]
