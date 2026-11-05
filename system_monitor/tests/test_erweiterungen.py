"""Tests für Laufwerke, WLAN/Traffic, Bluetooth, winget und Hintergrund-Threads.
Die Windows-Ausgaben (netsh, winget, PowerShell) werden als Beispieltexte nachgestellt."""
import time
from collections import namedtuple

import pytest

from monitor import bluetooth, network, updates
from monitor.cli import render_bluetooth, render_drives, render_traffic, render_updates, render_wlan
from monitor.drives import DriveScanner, is_external, list_drives
from monitor.network import TrafficMeter, format_bytes, format_rate, needs_location_permission, \
    parse_netsh_interfaces
from monitor.tasks import BackgroundRunner
from monitor.updates import build_upgrade_command, parse_winget_upgrade
from monitor.winutil import IS_WINDOWS, as_list, decode_output

# ---------------------------------------------------------------- Beispielausgaben
NETSH_DE = """
Es ist 1 Schnittstelle auf dem System vorhanden:

    Name                   : WLAN
    Beschreibung           : Intel(R) Wi-Fi 6 AX201 160MHz
    GUID                   : 0f1e2d3c-4b5a-6978-8796-a5b4c3d2e1f0
    Physische Adresse      : 12:34:56:78:9a:bc
    Schnittstellentyp      : Primär
    Status                 : Verbunden
    SSID                   : GFN-Gast
    AP BSSID               : aa:bb:cc:dd:ee:ff
    Band                   : 5 GHz
    Kanal                  : 36
    Netzwerktyp            : Infrastruktur
    Funktyp                : 802.11ax
    Authentifizierung      : WPA2-Personal
    Verschlüsselung        : CCMP
    Verbindungsmodus       : Automatische Verbindung
    Empfangsrate (MBit/s)  : 1201
    Übertragungsrate (MBit/s) : 864
    Signal                 : 87%
    Profil                 : GFN-Gast

    Status des gehosteten Netzwerks  : Nicht verfügbar
"""

NETSH_EN = """
There are 2 interfaces on the system:

    Name                   : Wi-Fi
    Description            : Realtek RTL8822CE
    State                  : connected
    SSID                   : HomeNet
    Radio type             : 802.11ac
    Channel                : 6
    Receive rate (Mbps)    : 400
    Transmit rate (Mbps)   : 300
    Signal                 : 54%

    Name                   : Wi-Fi 2
    Description            : USB WLAN Stick
    State                  : disconnected
"""

NETSH_LOCATION = """There is 1 interface on the system:
Network shell commands need location permission to access WLAN information. Turn on Location services on the Location page in Privacy & security settings.

Here is the URI for the Location page in the Settings app:
ms-settings:privacy-location
"""

WINGET_DE = (
    "   - \r   \\ \r   | \r"
    "Name                       ID                       Version      Verfügbar    Quelle\n"
    "---------------------------------------------------------------------------------------\n"
    "Mozilla Firefox (x64 de)   Mozilla.Firefox.de       131.0        132.0.1      winget\n"
    "7-Zip 23.01 (x64)          7zip.7zip                23.01        24.08        winget\n"
    "Notepad++ (64-bit x64)     Notepad++.Notepad++      8.6.9        8.7          winget\n"
    "3 Aktualisierungen verfügbar.\n"
    "\n"
    "Die folgenden Pakete haben ein Upgrade, erfordern jedoch explizite Zielversionen:\n"
    "Name     ID          Version  Verfügbar Quelle\n"
    "-----------------------------------------------\n"
    "Discord  Discord.Discord  1.0  1.1  winget\n"
)

WINGET_EN = (
    "Name                         Id                        Version    Available  Source\n"
    "------------------------------------------------------------------------------------\n"
    "Microsoft Visual Studio Code Microsoft.VisualStudioCode 1.94.0     1.95.1     winget\n"
    "1 upgrades available.\n"
)

WINGET_NONE = "   - \r\nEs wurde kein installiertes Paket gefunden, das den Eingabekriterien entspricht.\r\n"


# ---------------------------------------------------------------- WLAN
def test_netsh_deutsch():
    (info,) = parse_netsh_interfaces(NETSH_DE)
    assert info.name == "WLAN" and info.ssid == "GFN-Gast" and info.connected
    assert info.signal == 87 and info.radio == "802.11ax" and info.channel == "36"
    assert info.rx_mbit == "1201" and info.tx_mbit == "864" and info.auth == "WPA2-Personal"
    assert info.description.startswith("Intel")


def test_netsh_englisch_mehrere_adapter():
    a, b = parse_netsh_interfaces(NETSH_EN)
    assert (a.name, a.ssid, a.signal, a.connected) == ("Wi-Fi", "HomeNet", 54, True)
    assert a.rx_mbit == "400" and a.tx_mbit == "300"
    assert b.name == "Wi-Fi 2" and not b.connected and b.signal is None


def test_netsh_standortberechtigung_erkannt():
    assert needs_location_permission(NETSH_LOCATION)
    assert not needs_location_permission(NETSH_DE)
    assert parse_netsh_interfaces(NETSH_LOCATION) == []


def test_netsh_mit_oem_codepage():
    raw = NETSH_DE.encode("cp850")          # so liefert netsh unter deutschem Windows
    (info,) = parse_netsh_interfaces(decode_output(raw))
    assert info.tx_mbit == "864"            # Schlüssel "Übertragungsrate" korrekt erkannt


# ---------------------------------------------------------------- Traffic
Counter = namedtuple("Counter", "bytes_recv bytes_sent")


class FakeNet:
    def __init__(self):
        self.t = 0.0
        self.data = {"WLAN": Counter(1000, 500), "Ethernet": Counter(10, 10),
                     "Loopback Pseudo-Interface 1": Counter(9e9, 9e9)}

    def counters(self):
        return dict(self.data)

    def clock(self):
        return self.t


def test_traffic_raten_und_summen():
    net = FakeNet()
    m = TrafficMeter(history=5, counters=net.counters, clock=net.clock)
    first = m.sample("WLAN")
    assert first.down_bps == 0 and first.up_bps == 0
    net.t, net.data["WLAN"] = 2.0, Counter(1000 + 4096, 500 + 2048)
    s = m.sample("WLAN")
    assert s.down_bps == 2048 and s.up_bps == 1024
    assert s.total_down == 4096 and s.total_up == 2048
    assert len(m.history) == 2


def test_traffic_zaehler_reset_ergibt_keine_negativen_werte():
    net = FakeNet()
    m = TrafficMeter(counters=net.counters, clock=net.clock)
    m.sample("WLAN")
    net.t, net.data["WLAN"] = 1.0, Counter(10, 10)
    s = m.sample("WLAN")
    assert s.down_bps == 0 and s.up_bps == 0


def test_traffic_kartenwahl():
    net = FakeNet()
    m = TrafficMeter(counters=net.counters, clock=net.clock)
    assert "Loopback Pseudo-Interface 1" not in m.interfaces()
    assert m.guess_wlan() == "WLAN"
    assert m.guess_wlan(["Ethernet"]) == "Ethernet"      # gemeldeter Name hat Vorrang
    assert m.busiest() == "WLAN"
    assert m.sample("gibt-es-nicht") is None


def test_formatierung():
    assert format_rate(512) == "0.5 KB/s"
    assert format_rate(3 * 1024 ** 2) == "3.00 MB/s"
    assert format_bytes(500) == "500 B" and format_bytes(1536) == "1.5 KB"


# ---------------------------------------------------------------- winget
def test_winget_deutsch_mit_fortschrittsanzeige():
    ups = parse_winget_upgrade(WINGET_DE)
    assert [u.package_id for u in ups] == ["Mozilla.Firefox.de", "7zip.7zip", "Notepad++.Notepad++"]
    ff = ups[0]
    assert (ff.name, ff.installed, ff.available, ff.source) == ("Mozilla Firefox (x64 de)", "131.0", "132.0.1", "winget")


def test_winget_englisch():
    (u,) = parse_winget_upgrade(WINGET_EN)
    assert u.package_id == "Microsoft.VisualStudioCode" and u.available == "1.95.1"


def test_winget_keine_updates():
    assert parse_winget_upgrade(WINGET_NONE) == []


def test_upgrade_befehl():
    cmd = build_upgrade_command(["7zip.7zip", "Notepad++.Notepad++"])
    assert "winget upgrade --id 7zip.7zip -e" in cmd and "--accept-package-agreements" in cmd
    assert cmd.count("winget upgrade") == 2 and cmd.endswith("pause")
    assert build_upgrade_command(None).startswith("winget upgrade --all")


def test_upgrade_befehl_lehnt_gefaehrliche_ids_ab():
    with pytest.raises(ValueError):
        build_upgrade_command(["7zip.7zip & del C:\\*"])


# ---------------------------------------------------------------- Bluetooth
def test_bluetooth_json_einzelobjekte_und_listen():
    data = {"Adapter": {"Name": "Intel(R) Wireless Bluetooth(R)", "Status": "OK"},
            "Geraete": [
                {"Name": "Logitech MX Keys", "Typ": "LE", "Status": "OK", "Verbunden": False},
                {"Name": "Sony WH-1000XM4", "Typ": "Classic", "Status": "OK", "Verbunden": True},
                {"Name": "Altes Headset", "Typ": "Classic", "Status": "Unknown", "Verbunden": None}]}
    st = bluetooth.parse_bluetooth_json(data)
    assert st.adapters == [("Intel(R) Wireless Bluetooth(R)", "OK")]
    assert st.devices[0].name == "Sony WH-1000XM4" and st.devices[0].connection_text == "verbunden"
    assert {d.connection_text for d in st.devices} == {"verbunden", "nicht verbunden", "unbekannt"}
    assert st.message == ""


def test_bluetooth_ohne_adapter():
    st = bluetooth.parse_bluetooth_json({"Adapter": [], "Geraete": []})
    assert st.adapters == [] and "Kein Bluetooth-Adapter" in st.message


def test_as_list():
    assert as_list(None) == [] and as_list({"a": 1}) == [{"a": 1}] and as_list([1, 2]) == [1, 2]


# ---------------------------------------------------------------- Laufwerke
def test_extern_erkennung():
    assert is_external("rw,removable", "")
    assert is_external("rw,fixed", "USB")          # externe USB-Festplatte meldet sich als 'fixed'
    assert not is_external("rw,fixed", "NVMe")


def test_laufwerksliste_plausibel():
    drives = list_drives()
    assert drives, "mindestens das Systemlaufwerk muss gefunden werden"
    for d in drives:
        assert 0 <= d.percent <= 100 and d.total_gb > 0


def test_scanner_fragt_bus_typ_nur_bei_aenderung():
    calls = []
    scanner = DriveScanner(bus_lookup=lambda: calls.append(1) or {})
    scanner.scan()
    scanner.scan()
    scanner.scan()
    assert len(calls) == 1


# ---------------------------------------------------------------- Hintergrund
def test_background_runner():
    runner, got = BackgroundRunner(), []
    assert runner.submit("x", lambda: 42, got.append)
    assert not runner.submit("x", lambda: 0, got.append)      # läuft schon -> kein zweiter Start
    for _ in range(100):
        if runner.poll():
            break
        time.sleep(0.01)
    assert got == [42] and not runner.is_running("x")


def test_background_runner_fehler_wird_uebergeben():
    runner, got = BackgroundRunner(), []
    runner.submit("y", lambda: 1 / 0, got.append)
    for _ in range(100):
        if runner.poll():
            break
        time.sleep(0.01)
    assert isinstance(got[0], ZeroDivisionError)


# ---------------------------------------------------------------- Nicht-Windows / Ausgabe
@pytest.mark.skipif(IS_WINDOWS, reason="prüft das Verhalten außerhalb von Windows")
def test_ohne_windows_freundliche_meldungen():
    assert "Windows" in network.get_wlan_status().message
    assert "Windows" in bluetooth.get_bluetooth_status().message
    assert "Windows" in updates.list_updates().message


def test_cli_ausgaben():
    assert "LAUFWERKE" in render_drives(list_drives())
    assert "keine Netzwerkkarte" in render_traffic(None)
    assert "GFN-Gast" in render_wlan(network.WlanStatus(parse_netsh_interfaces(NETSH_DE)))
    assert "Sony" in render_bluetooth(bluetooth.parse_bluetooth_json(
        {"Adapter": {"Name": "A", "Status": "OK"}, "Geraete": {"Name": "Sony", "Typ": "LE", "Verbunden": True}}))
    assert "7zip.7zip" in render_updates(updates.UpdateResult(parse_winget_upgrade(WINGET_DE), "3"))
