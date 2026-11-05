"""Rauchtest der Oberfläche. Wird übersprungen, wenn kein Bildschirm bzw. kein tkinter vorhanden ist."""
import time
from dataclasses import replace

import pytest

tk = pytest.importorskip("tkinter")

from monitor.config import Config  # noqa: E402
from monitor.core import Monitor  # noqa: E402
from monitor.overlay_logic import OVERLAY_STYLES  # noqa: E402


@pytest.fixture
def app(tmp_path):
    from monitor import gui
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("kein Bildschirm verfügbar")
    cfg = replace(Config(), log_dir=str(tmp_path), csv_logging=False, interval_s=0.5, process_interval_s=1,
                  overlay_hide_main=False)
    application = gui.MonitorApp(root, Monitor(cfg, tmp_path), tmp_path / "config.json")
    application.process_calls = []
    orig = application.monitor.collector._top_processes
    application.monitor.collector._top_processes = lambda: application.process_calls.append(1) or orig()
    yield application
    try:
        application.quit()
    except tk.TclError:
        pass


def pump(app, seconds):
    end = time.time() + seconds
    while time.time() < end:
        app.root.update()
        time.sleep(0.01)


def test_messung_erscheint_in_der_oberflaeche(app):
    pump(app, 2.5)
    assert app.pct_lbl["RAM"].cget("text") != "–"
    assert app._last_snapshot is not None


def test_prozessliste_nur_in_der_uebersicht(app):
    from monitor import gui
    pump(app, 2.5)
    assert app.process_calls, "in der Übersicht wird die Prozessliste erstellt"
    app.select_view(gui.TAB_DRIVES)
    pump(app, 0.6)
    before = len(app.process_calls)
    pump(app, 3.0)                                  # Intervall 1 s längst abgelaufen
    assert len(app.process_calls) == before


def test_meldungsliste_ist_begrenzt(app):
    from monitor import gui
    for i in range(gui.MAX_ALERTS + 25):
        app._add_message(f"m{i}", "#ffffff")
    assert app.alert_list.size() == gui.MAX_ALERTS
    assert app.alert_list.get(app.alert_list.size() - 1) == f"m{gui.MAX_ALERTS + 24}"


@pytest.mark.parametrize("style", OVERLAY_STYLES)
def test_overlay_in_allen_stilen(app, style):
    app.monitor.apply_config(replace(app.monitor.config, overlay_style=style))
    pump(app, 1.5)
    app.toggle_overlay()
    pump(app, 1.0)
    assert app.overlay.visible
    ov = app.overlay
    if style == "tile":
        assert ov.pct_lbl["RAM"].cget("text").endswith("%") and ov.down_lbl.cget("text").startswith("↓")
    elif style == "numbers":
        assert "·" in ov.label.cget("text")
    else:
        assert ov.label.cget("text").startswith("CPU")
    app.toggle_overlay()
    assert not app.overlay.visible


def test_stilwechsel_bei_sichtbarem_overlay(app):
    pump(app, 1.5)
    app.toggle_overlay()
    app.monitor.apply_config(replace(app.monitor.config, overlay_style="tile"))
    app.overlay.apply_config(app.monitor.config)
    pump(app, 1.0)
    assert hasattr(app.overlay, "bar")


def test_hauptfenster_versteckt_zeichnet_nichts_und_scannt_nicht(app):
    pump(app, 2.0)
    app.monitor.apply_config(replace(app.monitor.config, overlay_hide_main=True))
    app._hotkey_ok = True                           # Tastenkürzel gilt als vorhanden (unter Linux gibt es keins)
    app.toggle_overlay()
    pump(app, 0.5)
    assert app._minimized() and app.root.state() == "withdrawn"
    n = len(app.process_calls)
    pump(app, 3.0)
    assert len(app.process_calls) == n
    assert app.overlay.visible
    app._hotkey_events.put("toggle")                # Tastenkürzel zurück
    pump(app, 0.5)
    assert not app.overlay.visible and app.root.state() == "normal"
