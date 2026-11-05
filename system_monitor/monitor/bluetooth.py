"""Bluetooth-Adapter und gekoppelte Geräte (über PowerShell Get-PnpDevice).

Hinweis: Windows bietet keinen dokumentierten Weg, den Verbindungsstatus eines Geräts
per PowerShell abzufragen. Verwendet wird die (undokumentierte) Geräteeigenschaft
{83DA6326-97A6-4088-9453-A1923F573B29} 15, die in Praxistests bei Verbindung True ist.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from .winutil import IS_WINDOWS, as_list, run_powershell_json

log = logging.getLogger(__name__)

CONNECTED_KEY = "{83DA6326-97A6-4088-9453-A1923F573B29} 15"

PS_SCRIPT = r"""
$all = Get-PnpDevice -Class Bluetooth
$adapter = $all | Where-Object { $_.InstanceId -match '^(USB|PCI|ACPI)\\' } |
    ForEach-Object { [pscustomobject]@{ Name = $_.FriendlyName; Status = [string]$_.Status } }
$devices = $all | Where-Object { $_.InstanceId -match '^(BTHENUM|BTHLE)\\DEV_' } | ForEach-Object {
    $p = Get-PnpDeviceProperty -InstanceId $_.InstanceId | Where-Object KeyName -eq '%KEY%'
    [pscustomobject]@{
        Name      = $_.FriendlyName
        Typ       = $(if ($_.InstanceId -like 'BTHLE*') { 'LE' } else { 'Classic' })
        Status    = [string]$_.Status
        Verbunden = $(if ($null -eq $p) { $null } else { [bool]$p.Data })
    }
}
[pscustomobject]@{ Adapter = @($adapter); Geraete = @($devices) } | ConvertTo-Json -Depth 3 -Compress
""".replace("%KEY%", CONNECTED_KEY)


@dataclass(frozen=True)
class BtDevice:
    name: str
    kind: str                  # Classic / LE
    status: str                # PnP-Status (OK = gekoppelt und Treiber aktiv)
    connected: bool | None     # None = unbekannt

    @property
    def connection_text(self) -> str:
        return {True: "verbunden", False: "nicht verbunden", None: "unbekannt"}[self.connected]


@dataclass
class BluetoothStatus:
    adapters: list[tuple[str, str]] = field(default_factory=list)   # (Name, Status)
    devices: list[BtDevice] = field(default_factory=list)
    message: str = ""


def parse_bluetooth_json(data) -> BluetoothStatus:
    if not data:
        return BluetoothStatus(message="Keine Bluetooth-Daten erhalten.")
    adapters = [(a.get("Name") or "?", a.get("Status") or "") for a in as_list(data.get("Adapter"))]
    devices = [BtDevice(d.get("Name") or "?", d.get("Typ") or "", d.get("Status") or "", d.get("Verbunden"))
               for d in as_list(data.get("Geraete"))]
    # dasselbe Gerät kann als Classic- und LE-Eintrag auftauchen -> verbunden zuerst
    devices.sort(key=lambda d: (d.connected is not True, d.name.lower()))
    msg = "" if adapters else "Kein Bluetooth-Adapter gefunden."
    return BluetoothStatus(adapters, devices, msg)


def get_bluetooth_status() -> BluetoothStatus:
    if not IS_WINDOWS:
        return BluetoothStatus(message="Bluetooth-Abfrage ist nur unter Windows verfügbar.")
    try:
        return parse_bluetooth_json(run_powershell_json(PS_SCRIPT, timeout=45))
    except Exception as exc:
        log.warning("Bluetooth-Abfrage fehlgeschlagen: %s", exc)
        return BluetoothStatus(message=f"Bluetooth-Abfrage fehlgeschlagen: {exc}")
