from types import SimpleNamespace

from netbox_unifi_sync.services import sync_engine


class FakeInterfaceEndpoint:
    def __init__(self, existing=None, fail_create=False):
        self.existing = existing
        self.fail_create = fail_create
        self.create_calls = []
        self.get_calls = []

    def get(self, **kwargs):
        self.get_calls.append(dict(kwargs))
        return self.existing

    def create(self, payload):
        self.create_calls.append(dict(payload))
        if self.fail_create:
            raise RuntimeError("duplicate key value violates unique constraint")
        return SimpleNamespace(id=99, name=payload["name"])


def test_create_or_get_interface_reuses_existing_interface():
    existing = SimpleNamespace(id=7, name="vlan.1")
    endpoint = FakeInterfaceEndpoint(existing=existing)
    nb = SimpleNamespace(dcim=SimpleNamespace(interfaces=endpoint))

    result, created = sync_engine._create_or_get_interface(
        nb,
        {"device": 42, "name": "vlan.1", "type": "virtual"},
    )

    assert result is existing
    assert created is False
    assert endpoint.create_calls == []


def test_create_or_get_interface_recovers_from_duplicate_create():
    existing = SimpleNamespace(id=7, name="vlan.1")
    endpoint = FakeInterfaceEndpoint(existing=None, fail_create=True)
    nb = SimpleNamespace(dcim=SimpleNamespace(interfaces=endpoint))

    def get_after_create(**kwargs):
        endpoint.get_calls.append(dict(kwargs))
        return None if len(endpoint.get_calls) == 1 else existing

    endpoint.get = get_after_create

    result, created = sync_engine._create_or_get_interface(
        nb,
        {"device": 42, "name": "vlan.1", "type": "virtual"},
    )

    assert result is existing
    assert created is False
    assert endpoint.create_calls == [{"device": 42, "name": "vlan.1", "type": "virtual"}]


def test_writable_specs_cache_path_falls_back_to_env_path(tmp_path, monkeypatch):
    source_path = tmp_path / "readonly" / "ubiquiti_device_specs.json"
    cache_path = tmp_path / "cache" / "ubiquiti_device_specs.json"
    monkeypatch.setenv("UNIFI_SPECS_CACHE_FILE", str(cache_path))
    monkeypatch.setattr(sync_engine.os, "access", lambda path, mode: str(path) == str(cache_path.parent))

    assert sync_engine._writable_specs_cache_path(str(source_path)) == str(cache_path)
