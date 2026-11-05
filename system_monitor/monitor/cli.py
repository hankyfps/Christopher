"""Terminal-Modus (ohne Fenster)."""
from __future__ import annotations

import os
import time

from .alerts import Alert
from .bluetooth import BluetoothStatus, get_bluetooth_status
from .collector import Snapshot, format_uptime
from .core import Monitor
from .drives import DriveInfo, DriveScanner
from .network import TrafficMeter, TrafficSample, WlanStatus, format_bytes, format_rate, get_wlan_status
from .updates import UpdateResult, list_updates


def bar(percent: float, width: int = 30) -> str:
    filled = round(percent / 100 * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def render(s: Snapshot, thresholds: dict[str, float], history: list[Alert], extras: str = "") -> str:
    lines = [
        f"SYSTEM-MONITOR   {s.timestamp:%d.%m.%Y %H:%M:%S}   Laufzeit: {format_uptime(s.uptime_s)}",
        "=" * 78,
        f"CPU        {bar(s.cpu_percent)} {s.cpu_percent:5.1f} %  ({s.cpu_cores} Kerne)",
        f"RAM        {bar(s.ram_percent)} {s.ram_percent:5.1f} %  ({s.ram_used_gb:.1f} / {s.ram_total_gb:.1f} GB)",
        f"Festplatte {bar(s.disk_percent)} {s.disk_percent:5.1f} %  "
        f"({s.disk_used_gb:.0f} / {s.disk_total_gb:.0f} GB, {s.disk_path})",
        "Schwellen: " + ", ".join(f"{k} {v:.0f} %" for k, v in thresholds.items()),
        "",
        f"{'PID':>7}  {'Prozess':<28} {'CPU %':>6} {'RAM %':>6} {'RAM MB':>8}",
        "-" * 60,
    ]
    for p in s.processes:
        lines.append(f"{p.pid:>7}  {p.name[:28]:<28} {p.cpu_percent:6.1f} {p.memory_percent:6.1f} {p.memory_mb:8.0f}")
    if extras:
        lines += ["", extras]
    lines += ["", "Letzte Meldungen:"]
    lines += [f"  {a.message()}" for a in history[-5:]] or ["  (keine)"]
    return "\n".join(lines)


def render_drives(drives: list[DriveInfo]) -> str:
    lines = ["LAUFWERKE", f"{'Laufwerk':<14}{'Typ':<20}{'FS':<8}{'Belegt':>10}{'Gesamt':>10}{'Belegung':>10}"]
    for d in drives:
        lines.append(f"{d.mountpoint[:13]:<14}{d.kind[:19]:<20}{d.fstype[:7]:<8}"
                     f"{d.used_gb:8.1f} GB{d.total_gb:8.1f} GB{d.percent:8.1f} %")
    return "\n".join(lines)


def render_traffic(sample: TrafficSample | None) -> str:
    if sample is None:
        return "NETZWERK  keine Netzwerkkarte gefunden"
    return (f"NETZWERK  {sample.nic}:  ↓ {format_rate(sample.down_bps)}   ↑ {format_rate(sample.up_bps)}   "
            f"(gesamt ↓ {format_bytes(sample.total_down)} / ↑ {format_bytes(sample.total_up)})")


def render_wlan(status: WlanStatus) -> str:
    lines = ["WLAN"]
    for i in status.interfaces:
        sig = f"{i.signal} %" if i.signal is not None else "–"
        lines.append(f"  {i.name}: {i.state}  SSID: {i.ssid or '–'}  Signal: {sig}  {i.radio}")
    if status.message:
        lines.append(f"  Hinweis: {status.message}")
    return "\n".join(lines)


def render_bluetooth(status: BluetoothStatus) -> str:
    lines = ["BLUETOOTH"]
    lines += [f"  Adapter: {n} ({s})" for n, s in status.adapters]
    lines += [f"  {d.name[:40]:<40} {d.kind:<8} {d.connection_text}" for d in status.devices]
    if status.message:
        lines.append(f"  Hinweis: {status.message}")
    return "\n".join(lines)


def render_updates(result: UpdateResult) -> str:
    lines = ["UPDATES (winget)", f"  {result.message}"]
    for u in result.updates:
        lines.append(f"  {u.name[:34]:<34} {u.package_id[:30]:<30} {u.installed:>12} -> {u.available}")
    return "\n".join(lines)


def _pick_nic(meter: TrafficMeter, configured: str, wlan: WlanStatus | None = None) -> str | None:
    names = meter.interfaces()
    if configured in names:
        return configured
    preferred = [i.name for i in wlan.interfaces] if wlan else []
    return meter.guess_wlan(preferred) or meter.busiest()


def run_cli(monitor: Monitor, once: bool = False, updates: bool = False) -> None:
    if updates:
        print("Suche Updates mit winget …")
        print(render_updates(list_updates()))
        return

    scanner = DriveScanner()
    meter = TrafficMeter()
    history: list[Alert] = []
    if once:
        # Vormessung + 1 s warten: die erste CPU-Messung (System und Prozesse) ist immer 0
        wlan = get_wlan_status()
        nic = _pick_nic(meter, monitor.config.net_interface, wlan)
        monitor.collector.snapshot()
        if nic:
            meter.sample(nic)
        time.sleep(1.0)
        snap, alerts = monitor.step(force_processes=True)
        extras = "\n\n".join([render_drives(scanner.scan()),
                              render_traffic(meter.sample(nic) if nic else None),
                              render_wlan(wlan), render_bluetooth(get_bluetooth_status())])
        print(render(snap, monitor.config.thresholds(), alerts, extras))
        return

    nic = _pick_nic(meter, monitor.config.net_interface)
    drives: list[DriveInfo] = []
    last_scan = -1e9
    try:
        while True:
            snap, alerts = monitor.step()
            history.extend(alerts)
            if time.monotonic() - last_scan >= monitor.config.drive_refresh_s:
                drives, last_scan = scanner.scan(), time.monotonic()
            extras = render_drives(drives) + "\n\n" + render_traffic(meter.sample(nic) if nic else None)
            os.system("cls" if os.name == "nt" else "clear")
            if alerts:
                print("\a", end="")          # Signalton bei neuer Meldung
            print(render(snap, monitor.config.thresholds(), history, extras))
            print("\n[Strg+C] beendet das Programm")
            time.sleep(monitor.config.interval_s)
    except KeyboardInterrupt:
        print("\nBeendet.")
