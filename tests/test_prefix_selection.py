from types import SimpleNamespace

from netbox_unifi_sync.services import sync_engine


class FakeListEndpoint:
    def __init__(self, items):
        self._items = list(items)

    def all(self):
        return list(self._items)


class FakePrefixEndpoint:
    def __init__(self, prefixes):
        self._prefixes = list(prefixes)

    def filter(self, **kwargs):
        return list(self._prefixes)


class FakeIPAddressObject:
    def __init__(self, payload):
        self.address = payload["address"]
        self.tags = []
        self.saved = False

    def save(self):
        self.saved = True


class FakeIPAddressEndpoint:
    def __init__(self):
        self.create_calls = []

    def get(self, **kwargs):
        return None

    def create(self, payload):
        self.create_calls.append(dict(payload))
        return FakeIPAddressObject(payload)


class FakeInterfaceEndpoint:
    def filter(self, **kwargs):
        return [SimpleNamespace(id=7)]


class FakeNetBox:
    def __init__(self, prefixes):
        self.ipam = SimpleNamespace(
            prefixes=FakePrefixEndpoint(prefixes),
            ip_addresses=FakeIPAddressEndpoint(),
        )
        self.dcim = SimpleNamespace(interfaces=FakeInterfaceEndpoint())


def test_sync_client_ips_uses_most_specific_matching_prefix(monkeypatch):
    monkeypatch.setenv("SYNC_CLIENT_IPS", "true")
    monkeypatch.setattr(sync_engine, "ensure_tag", lambda *args, **kwargs: SimpleNamespace(id=123))

    nb = FakeNetBox([
        SimpleNamespace(prefix="10.0.0.0/24"),
        SimpleNamespace(prefix="10.0.0.8/29"),
    ])
    site_obj = SimpleNamespace(client=FakeListEndpoint([
        {
            "macAddress": "aa:bb:cc:dd:ee:ff",
            "ipAddress": "10.0.0.10",
            "name": "printer-01",
        }
    ]))

    sync_engine.sync_client_ips(
        nb,
        site_obj,
        SimpleNamespace(name="HQ", id=1),
        SimpleNamespace(id=42),
    )

    assert nb.ipam.ip_addresses.create_calls[0]["address"] == "10.0.0.10/29"
    assert nb.ipam.ip_addresses.create_calls[0]["description"] == (
        "unifi-client:AA:BB:CC:DD:EE:FF | UniFi client: printer-01 | IP: 10.0.0.10"
    )
