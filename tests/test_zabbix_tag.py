from types import SimpleNamespace

from netbox_unifi_sync.services import sync_engine


class _Device:
    def __init__(self, tags=None):
        self.tags = tags or []
        self.saves = 0

    def save(self):
        self.saves += 1


def _fake_tag(monkeypatch, calls):
    tag = SimpleNamespace(id=7)

    def ensure_tag(nb, name, slug=None, color=None):
        calls.append(name)
        return tag

    monkeypatch.setattr(sync_engine, "ensure_tag", ensure_tag)
    return tag


def test_zabbix_tag_added_by_default(monkeypatch):
    monkeypatch.delenv("SYNC_ZABBIX_TAG", raising=False)
    calls = []
    _fake_tag(monkeypatch, calls)
    device = _Device()
    sync_engine._ensure_zabbix_tag(None, device, "sw-01")
    assert calls == ["zabbix"]
    assert device.tags == [7]
    assert device.saves == 1


def test_zabbix_tag_not_duplicated(monkeypatch):
    monkeypatch.delenv("SYNC_ZABBIX_TAG", raising=False)
    _fake_tag(monkeypatch, [])
    device = _Device(tags=[SimpleNamespace(id=7)])
    sync_engine._ensure_zabbix_tag(None, device, "sw-01")
    assert device.saves == 0


def test_zabbix_tag_off(monkeypatch):
    monkeypatch.setenv("SYNC_ZABBIX_TAG", "false")
    calls = []
    _fake_tag(monkeypatch, calls)
    device = _Device()
    sync_engine._ensure_zabbix_tag(None, device, "sw-01")
    assert calls == []
    assert device.tags == []
    assert device.saves == 0
