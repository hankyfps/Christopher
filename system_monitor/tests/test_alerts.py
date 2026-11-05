from monitor.alerts import AlertManager, Level


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def make(cooldown=60, hysteresis=5):
    clock = FakeClock()
    return AlertManager({"CPU": 80}, cooldown, hysteresis, clock=clock), clock


def test_unter_schwelle_keine_meldung():
    am, _ = make()
    assert am.check({"CPU": 79.9}) == []


def test_warnung_ab_schwelle():
    am, _ = make()
    alerts = am.check({"CPU": 80.0})
    assert len(alerts) == 1 and alerts[0].level is Level.WARNUNG
    assert am.is_active("CPU")


def test_cooldown_unterdrueckt_wiederholung():
    am, clock = make(cooldown=60)
    am.check({"CPU": 90})
    clock.t = 30
    assert am.check({"CPU": 95}) == []


def test_wiederholung_nach_cooldown():
    am, clock = make(cooldown=60)
    am.check({"CPU": 90})
    clock.t = 60
    alerts = am.check({"CPU": 90})
    assert len(alerts) == 1 and alerts[0].level is Level.WARNUNG


def test_hysterese_keine_entwarnung_knapp_unter_schwelle():
    am, _ = make(hysteresis=5)
    am.check({"CPU": 90})
    assert am.check({"CPU": 77}) == []          # 77 >= 80 - 5
    assert am.is_active("CPU")


def test_entwarnung_unter_hysterese():
    am, _ = make(hysteresis=5)
    am.check({"CPU": 90})
    alerts = am.check({"CPU": 74})
    assert len(alerts) == 1 and alerts[0].level is Level.OK
    assert not am.is_active("CPU")


def test_unbekannte_kennzahl_wird_ignoriert():
    am, _ = make()
    assert am.check({"GPU": 100}) == []


def test_meldungstext():
    am, _ = make()
    msg = am.check({"CPU": 91.25})[0].message()
    assert "WARNUNG" in msg and "CPU" in msg and "91.2" in msg
