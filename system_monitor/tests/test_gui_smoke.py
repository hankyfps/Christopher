"""Rauchtest der Oberfläche. Wird übersprungen, wenn kein Bildschirm bzw. kein tkinter vorhanden ist."""
import time
from dataclasses import replace

import pytest

tk = pytest.importorskip("tkinter")

from monitor.config import Config  # noqa: E402
from monitor.core import Monitor  # noqa: E402


@pytest.fixture
def app(tmp_path):
    from monitor import gui
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("kein Bildschirm verfügbar")
    cfg = replace(Config(), log_dir=str(tmp_path), csv_logging=False, interval_s=0.5, overlay_hide_main=False)
    application = gui.MonitorApp(root, Monitor(cfg, tmp_path), tmp_path / "config.json")
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


def test_messung_erscheint_in_der_kopfzeile(app):
    pump(app, 2.5)
    assert app.value_labels["RAM"].cget("text") != "–"
    assert app._last_snap is not None


def test_prozessliste_nur_auf_tab_uebersicht(app):
    from monitor import gui
    pump(app, 2.0)
    app.notebook.select(gui.TAB_DRIVES)
    app.root.update()
    assert app._processes_wanted() is False
    app.notebook.select(gui.TAB_OVERVIEW)
    app.root.update()
    assert app._processes_wanted() is True


def test_meldungsliste_ist_begrenzt(app):
    from monitor import gui
    for i in range(gui.MAX_ALERTS + 25):
        app._add_message(f"m{i}", "#ffffff")
    assert app.alert_list.size() == gui.MAX_ALERTS
    assert app.alert_list.get(app.alert_list.size() - 1) == f"m{gui.MAX_ALERTS + 24}"


def test_overlay_ein_und_aus(app):
    pump(app, 1.5)
    app.toggle_overlay()
    pump(app, 1.0)
    assert app.overlay.visible and app.overlay.label.cget("text").startswith("CPU")
    app.toggle_overlay()
    assert not app.overlay.visible
