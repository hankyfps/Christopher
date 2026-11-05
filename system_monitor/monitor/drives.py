"""Alle Laufwerke inkl. externer Speichermedien (USB-Stick, externe Festplatte, SD-Karte)."""
from __future__ import annotations

import logging
from dataclasses import dataclass

import psutil

from .winutil import IS_WINDOWS, as_list, run_powershell_json

log = logging.getLogger(__name__)
GB = 1024 ** 3

# Bus-Typen, die als "extern" gelten (Werte von Get-Disk -> BusType)
EXTERNAL_BUS_TYPES = {"USB", "SD", "MMC", "1394"}


@dataclass(frozen=True)
class DriveInfo:
    mountpoint: str        # z. B. "E:\\"
    fstype: str            # NTFS, FAT32, exFAT ...
    bus: str               # USB, NVMe, SATA ... oder "" wenn unbekannt
    external: bool
    total_gb: float
    used_gb: float
    free_gb: float
    percent: float

    @property
    def kind(self) -> str:
        if self.external:
            return f"extern ({self.bus})" if self.bus else "extern (wechselbar)"
        return f"intern ({self.bus})" if self.bus else "intern"


def get_bus_types() -> dict[str, str]:
    """Laufwerksbuchstabe -> Bus-Typ (USB, NVMe, SATA ...), über PowerShell Get-Disk.
    Liefert {} bei Fehlern oder außerhalb von Windows (dann zählt nur 'removable')."""
    if not IS_WINDOWS:
        return {}
    script = ("Get-Partition | Where-Object DriveLetter | ForEach-Object { "
              "[pscustomobject]@{L=[string]$_.DriveLetter; "
              "B=[string](Get-Disk -Number $_.DiskNumber).BusType} } | ConvertTo-Json -Compress")
    try:
        data = run_powershell_json(script, timeout=20)
    except Exception as exc:  # PowerShell fehlt, Zeitüberschreitung, ungültiges JSON ...
        log.warning("Bus-Typen der Laufwerke nicht ermittelbar: %s", exc)
        return {}
    return {f"{e['L'].upper()}:\\": e.get("B", "") for e in as_list(data) if e.get("L")}


def is_external(opts: str, bus: str) -> bool:
    return "removable" in opts.split(",") or bus.upper() in EXTERNAL_BUS_TYPES


def list_drives(bus_types: dict[str, str] | None = None) -> list[DriveInfo]:
    """Alle eingebundenen Laufwerke mit Speicherplatz. Leere Kartenleser/CD-Laufwerke werden übersprungen."""
    bus_types = bus_types or {}
    drives: list[DriveInfo] = []
    for part in psutil.disk_partitions(all=False):
        if "cdrom" in part.opts or not part.fstype:
            continue
        if not IS_WINDOWS and (part.fstype in ("squashfs", "tmpfs", "overlay")
                               or part.mountpoint.startswith(("/snap", "/boot/efi"))):
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except (PermissionError, OSError):          # kein Medium eingelegt o. Ä.
            continue
        bus = bus_types.get(part.mountpoint.upper(), "")
        drives.append(DriveInfo(
            mountpoint=part.mountpoint, fstype=part.fstype, bus=bus,
            external=is_external(part.opts, bus),
            total_gb=usage.total / GB, used_gb=usage.used / GB, free_gb=usage.free / GB,
            percent=usage.percent,
        ))
    drives.sort(key=lambda d: (d.external, d.mountpoint))
    return drives


class DriveScanner:
    """Liest die Laufwerke ein. Die langsame Bus-Abfrage (PowerShell) läuft nur,
    wenn sich die Menge der Laufwerke geändert hat (z. B. USB-Stick eingesteckt)."""

    def __init__(self, bus_lookup=get_bus_types) -> None:
        self._bus_lookup = bus_lookup
        self._bus: dict[str, str] = {}
        self._known: set[str] | None = None

    def scan(self) -> list[DriveInfo]:
        drives = list_drives(self._bus)
        mountpoints = {d.mountpoint.upper() for d in drives}
        if mountpoints != self._known:
            self._bus = self._bus_lookup()
            drives = list_drives(self._bus)
        self._known = mountpoints
        return drives
