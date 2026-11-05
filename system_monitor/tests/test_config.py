import json

import pytest

from monitor.config import Config


def test_standardwerte_gueltig():
    Config().validate()


def test_fehlende_datei_wird_angelegt(tmp_path):
    path = tmp_path / "config.json"
    cfg = Config.load(path)
    assert path.exists()
    assert cfg == Config()


def test_werte_werden_gelesen(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"cpu_threshold": 70, "interval_s": 5}), encoding="utf-8")
    cfg = Config.load(path)
    assert cfg.cpu_threshold == 70 and cfg.interval_s == 5
    assert cfg.ram_threshold == Config().ram_threshold      # fehlender Wert -> Standard


def test_unbekannte_schluessel_ignoriert(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"foo": 1, "cpu_threshold": 60}), encoding="utf-8")
    assert Config.load(path).cpu_threshold == 60


@pytest.mark.parametrize("inhalt", ["{kaputt", json.dumps({"cpu_threshold": 150}),
                                    json.dumps({"interval_s": 0.1})])
def test_ungueltige_datei_liefert_standard(tmp_path, inhalt):
    path = tmp_path / "config.json"
    path.write_text(inhalt, encoding="utf-8")
    assert Config.load(path) == Config()


def test_speichern_und_laden(tmp_path):
    path = tmp_path / "sub" / "config.json"
    Config(cpu_threshold=55, disk_path="/").save(path)
    cfg = Config.load(path)
    assert cfg.cpu_threshold == 55 and cfg.effective_disk_path == "/"


def test_speichern_ungueltig_wirft_fehler(tmp_path):
    with pytest.raises(ValueError):
        Config(top_processes=0).save(tmp_path / "c.json")
