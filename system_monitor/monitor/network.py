"""WLAN-Verbindung (netsh / Get-NetAdapter) und Netzwerk-Traffic (psutil)."""
from __future__ import annotations

import logging
import re
import time
from collections import deque
from dataclasses import dataclass, field

import psutil

from .winutil import IS_WINDOWS, NotSupportedError, as_list, run_command, run_powershell_json

log = logging.getLogger(__name__)

LOCATION_HINT = ("Windows gibt WLAN-Namen (SSID) nur mit Standortberechtigung heraus: "
                 "Einstellungen › Datenschutz und Sicherheit › Standort › "
                 "„Desktop-Apps Zugriff auf Ihren Standort erlauben“ einschalten.")


# ====================================================================== WLAN
@dataclass
class WlanInfo:
    name: str = ""            # Adaptername, z. B. "WLAN"
    description: str = ""     # z. B. "Intel(R) Wi-Fi 6 AX201"
    state: str = ""           # Verbunden / Getrennt
    ssid: str = ""
    signal: int | None = None
    radio: str = ""           # 802.11ax ...
    band: str = ""
    channel: str = ""
    rx_mbit: str = ""
    tx_mbit: str = ""
    auth: str = ""

    @property
    def connected(self) -> bool:
        return self.state.strip().lower() in ("verbunden", "connected", "up")


@dataclass
class WlanStatus:
    interfaces: list[WlanInfo] = field(default_factory=list)
    message: str = ""         # Hinweis/Fehler für die Anzeige


_LINE = re.compile(r"^\s*(.+?)\s+:\s?(.*)$")


def _field_for(key: str) -> str | None:
    k = key.strip().lower()
    simple = {
        "name": "name", "beschreibung": "description", "description": "description",
        "status": "state", "state": "state", "ssid": "ssid", "signal": "signal",
        "funktyp": "radio", "radio type": "radio", "band": "band",
        "kanal": "channel", "channel": "channel",
        "authentifizierung": "auth", "authentication": "auth",
    }
    if k in simple:
        return simple[k]
    if k.startswith(("empfangsrate", "receive rate")):
        return "rx_mbit"
    if k.startswith(("übertragungsrate", "transmit rate")) or ("rate" in k and "bertragung" in k):
        return "tx_mbit"
    return None


def parse_netsh_interfaces(text: str) -> list[WlanInfo]:
    """Wertet die Ausgabe von 'netsh wlan show interfaces' aus (deutsch oder englisch)."""
    result: list[WlanInfo] = []
    current: WlanInfo | None = None
    for line in text.splitlines():
        m = _LINE.match(line)
        if not m:
            continue
        attr = _field_for(m.group(1))
        if attr is None:
            continue
        value = m.group(2).strip()
        if attr == "name":
            current = WlanInfo(name=value)
            result.append(current)
            continue
        if current is None:
            continue
        if attr == "signal":
            digits = re.sub(r"\D", "", value)
            current.signal = int(digits) if digits else None
        else:
            setattr(current, attr, value)
    return result


def needs_location_permission(text: str) -> bool:
    t = text.lower()
    return "privacy-location" in t or "location permission" in t or "standortberechtigung" in t


def _wlan_adapters_powershell() -> list[WlanInfo]:
    """Fallback ohne Standortrecht: WLAN-Adapter über Get-NetAdapter (NdisPhysicalMedium 9 = 802.11)."""
    data = run_powershell_json(
        "Get-NetAdapter | Where-Object { $_.NdisPhysicalMedium -eq 9 } | "
        "Select-Object Name, InterfaceDescription, Status, LinkSpeed | ConvertTo-Json -Compress", timeout=20)
    return [WlanInfo(name=a.get("Name", ""), description=a.get("InterfaceDescription", ""),
                     state=a.get("Status", ""), rx_mbit=a.get("LinkSpeed", ""))
            for a in as_list(data)]


def get_wlan_status() -> WlanStatus:
    if not IS_WINDOWS:
        return WlanStatus(message="WLAN-Details sind nur unter Windows verfügbar.")
    try:
        res = run_command(["netsh", "wlan", "show", "interfaces"], timeout=15)
    except NotSupportedError as exc:
        return WlanStatus(message=str(exc))
    except Exception as exc:
        return WlanStatus(message=f"netsh fehlgeschlagen: {exc}")

    if needs_location_permission(res.output):
        try:
            adapters = _wlan_adapters_powershell()
        except Exception as exc:
            log.warning("Get-NetAdapter fehlgeschlagen: %s", exc)
            adapters = []
        return WlanStatus(adapters, LOCATION_HINT)

    interfaces = parse_netsh_interfaces(res.output)
    if not interfaces:
        first = next((ln.strip() for ln in res.output.splitlines() if ln.strip()), "")
        return WlanStatus(message=first or "Kein WLAN-Adapter gefunden.")
    return WlanStatus(interfaces)


# ====================================================================== Traffic
@dataclass(frozen=True)
class TrafficSample:
    nic: str
    down_bps: float          # Bytes pro Sekunde
    up_bps: float
    total_down: int          # Bytes seit Programmstart
    total_up: int


_WLAN_NAME = re.compile(r"wlan|wi-?fi|wireless|^wl", re.IGNORECASE)
_LOOPBACK = re.compile(r"loopback|^lo$", re.IGNORECASE)


class TrafficMeter:
    """Berechnet Up-/Download-Raten aus den Bytezählern einer Netzwerkkarte."""

    def __init__(self, history: int = 60, counters=None, clock=time.monotonic) -> None:
        self._counters = counters or (lambda: psutil.net_io_counters(pernic=True))
        self._clock = clock
        self.history: deque[tuple[float, float]] = deque(maxlen=history)   # (down, up)
        self._nic: str | None = None
        self._last: tuple[float, int, int] | None = None   # (Zeit, recv, sent)
        self._start: tuple[int, int] | None = None

    def read(self) -> dict:
        """Alle Bytezähler einmal lesen (kann an interfaces()/sample() weitergegeben werden)."""
        return self._counters()

    def interfaces(self, counters: dict | None = None) -> list[str]:
        counters = self._counters() if counters is None else counters
        return sorted(n for n in counters if not _LOOPBACK.search(n))

    def guess_wlan(self, preferred: list[str] | None = None) -> str | None:
        """Bevorzugt die von netsh/Get-NetAdapter gemeldeten Namen, sonst Namensmuster."""
        names = self.interfaces()
        for p in preferred or []:
            if p in names:
                return p
        return next((n for n in names if _WLAN_NAME.search(n)), None)

    def busiest(self) -> str | None:
        """Karte mit dem meisten Datenverkehr (z. B. LAN-Kabel am Desktop-PC)."""
        counters = {n: c for n, c in self._counters().items() if not _LOOPBACK.search(n)}
        if not counters:
            return None
        return max(counters, key=lambda n: counters[n].bytes_recv + counters[n].bytes_sent)

    def sample(self, nic: str, all_counters: dict | None = None) -> TrafficSample | None:
        counters = (self._counters() if all_counters is None else all_counters).get(nic)
        if counters is None:
            return None
        now = self._clock()
        recv, sent = counters.bytes_recv, counters.bytes_sent
        if nic != self._nic:                       # Karte gewechselt -> neu beginnen
            self._nic, self._last, self._start = nic, None, (recv, sent)
            self.history.clear()
        down = up = 0.0
        if self._last is not None:
            dt = now - self._last[0]
            if dt > 0:
                down = max(0, recv - self._last[1]) / dt     # max(): Zähler-Reset abfangen
                up = max(0, sent - self._last[2]) / dt
        self._last = (now, recv, sent)
        self.history.append((down, up))
        return TrafficSample(nic, down, up, max(0, recv - self._start[0]), max(0, sent - self._start[1]))


def format_rate(bps: float) -> str:
    if bps >= 1024 ** 2:
        return f"{bps / 1024 ** 2:.2f} MB/s"
    return f"{bps / 1024:.1f} KB/s"


def format_bytes(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.2f} TB"
