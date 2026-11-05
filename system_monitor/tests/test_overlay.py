"""Tests für die GUI-freie Logik des Overlays, die neuen Einstellungen und das Überspringen der Prozessliste."""
import json

import pytest

from monitor.collector import SystemCollector
from monitor.config import Config, default_disk_path
from monitor.core import Monitor
from monitor.overlay_logic import (MOD_ALT, MOD_CONTROL, MOD_SHIFT, MOD_WIN, POSITIONS, format_overlay_text,
                                   level_for, normalize_hotkey, overlay_geometry, parse_hotkey)


# ---------------------------------------------------------------- Position
def test_position_oben():
    assert overlay_geometry("top-left", 1920, 1080, 300, 30, margin=12) == (12, 12)
    assert overlay_geometry("top-center", 1920, 1080, 300, 30, margin=12) == ((1920 - 300) // 2, 12)
    assert overlay_geometry("top-right", 1920, 1080, 300, 30, margin=12) == (1920 - 300 - 12, 12)


def test_position_unten():
    assert overlay_geometry("bottom-left", 1920, 1080, 300, 30, 12) == (12, 1080 - 30 - 12)
    assert overlay_geometry("bottom-right", 1920, 1080, 300, 30, 12) == (1920 - 300 - 12, 1080 - 30 - 12)
    assert overlay_geometry("bottom-center", 1920, 1080, 300, 30, 12)[1] == 1080 - 30 - 12


def test_position_alle_gueltigen_liegen_im_bild():
    for pos in POSITIONS:
        x, y = overlay_geometry(pos, 1280, 720, 380, 28)
        assert 0 <= x <= 1280 - 380 and 0 <= y <= 720 - 28


def test_position_unbekannt():
    with pytest.raises(ValueError):
        overlay_geometry("mitte-links", 1920, 1080, 300, 30)


def test_position_groesser_als_bildschirm_bleibt_bei_null():
    x, y = overlay_geometry("top-right", 200, 100, 380, 28)
    assert x >= 0 and y >= 0


# ---------------------------------------------------------------- Text und Farbe
def test_overlay_text():
    text = format_overlay_text(23.4, 61.0, 1.5 * 1024 ** 2, 100 * 1024, "14:32")
    assert text == "CPU  23%  RAM  61%  ↓ 1.50 MB/s  ↑ 100.0 KB/s  14:32"


def test_overlay_text_rundet_und_begrenzt():
    assert format_overlay_text(99.6, 100.0, 0, 0, "00:00").startswith("CPU 100%  RAM 100%")


def test_level_for():
    assert level_for(50, 85) == "normal"
    assert level_for(75, 85) == "nah"          # innerhalb von 10 Punkten unter der Schwelle
    assert level_for(85, 85) == "alarm"
    assert level_for(100, 85) == "alarm"


# ---------------------------------------------------------------- Tastenkürzel
def test_hotkey_parsen():
    assert parse_hotkey("ctrl+alt+o") == (MOD_CONTROL | MOD_ALT, ord("O"))
    assert parse_hotkey("Strg + Shift + F9") == (MOD_CONTROL | MOD_SHIFT, 0x70 + 8)
    assert parse_hotkey("win+alt+7") == (MOD_WIN | MOD_ALT, ord("7"))


def test_hotkey_normalisieren():
    assert normalize_hotkey("  Strg+ALT+o ") == "ctrl+alt+o"
    assert normalize_hotkey("shift+ctrl+F1") == "ctrl+shift+f1"       # feste Reihenfolge


@pytest.mark.parametrize("bad", ["", "o", "ctrl+alt", "ctrl+alt+oo", "ctrl+alt+ö", "ctrl+f13", "ctrl+ctrl+o",
                                 "foo+o", "ctrl+alt+o+p"])
def test_hotkey_ungueltig(bad):
    with pytest.raises(ValueError):
        parse_hotkey(bad)


# ---------------------------------------------------------------- Einstellungen
def test_overlay_standardwerte():
    cfg = Config()
    cfg.validate()
    assert cfg.overlay_enabled is False
    assert cfg.overlay_position == "top-center"
    assert cfg.overlay_alpha == 0.7
    assert cfg.overlay_click_through is True
    assert cfg.overlay_hotkey == "ctrl+alt+o"
    assert cfg.overlay_hide_main is True
    assert cfg.process_interval_s == 15.0


@pytest.mark.parametrize("field, value", [
    ("overlay_alpha", 0.1), ("overlay_alpha", 1.1), ("overlay_position", "mitte"), ("overlay_hotkey", "o"),
])
def test_overlay_ungueltige_werte(field, value):
    cfg = Config(**{field: value})
    with pytest.raises(ValueError):
        cfg.validate()


def test_overlay_werte_werden_gespeichert_und_gelesen(tmp_path):
    path = tmp_path / "config.json"
    Config(overlay_enabled=True, overlay_position="bottom-right", overlay_alpha=0.5,
           overlay_click_through=False, overlay_hotkey="ctrl+shift+m", overlay_hide_main=False).save(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["overlay_position"] == "bottom-right"
    cfg = Config.load(path)
    assert cfg.overlay_enabled and cfg.overlay_alpha == 0.5 and not cfg.overlay_click_through
    assert cfg.overlay_hotkey == "ctrl+shift+m" and not cfg.overlay_hide_main


def test_alte_konfiguration_ohne_overlay_felder_bleibt_gueltig(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"cpu_threshold": 70}), encoding="utf-8")
    cfg = Config.load(path)
    assert cfg.cpu_threshold == 70 and cfg.overlay_hotkey == "ctrl+alt+o"


# ---------------------------------------------------------------- Prozessliste überspringen
class FakeClock:
    t = 0.0

    def __call__(self):
        return self.t


def test_skip_processes_baut_liste_nicht_neu():
    clock = FakeClock()
    c = SystemCollector(default_disk_path(), 5, process_interval_s=5, clock=clock)
    calls = []
    orig = c._top_processes
    c._top_processes = lambda: calls.append(1) or orig()
    first = c.snapshot()
    clock.t = 100                                   # Intervall längst abgelaufen
    skipped = c.snapshot(skip_processes=True)
    assert len(calls) == 1 and skipped.processes is first.processes
    again = c.snapshot()                            # wieder gebraucht -> sofort neu, weil veraltet
    assert len(calls) == 2 and again.processes is not skipped.processes


def test_skip_processes_gilt_nicht_bei_force():
    clock = FakeClock()
    c = SystemCollector(default_disk_path(), 5, process_interval_s=5, clock=clock)
    calls = []
    orig = c._top_processes
    c._top_processes = lambda: calls.append(1) or orig()
    c.snapshot(force_processes=True, skip_processes=True)
    assert len(calls) == 0                          # skip hat Vorrang (Fenster nicht sichtbar)


def test_monitor_reicht_skip_processes_weiter(tmp_path):
    mon = Monitor(Config(csv_logging=False), tmp_path)
    calls = []
    orig = mon.collector._top_processes
    mon.collector._top_processes = lambda: calls.append(1) or orig()
    mon.step(skip_processes=True)
    assert calls == []
    mon.step()
    assert calls == [1]
