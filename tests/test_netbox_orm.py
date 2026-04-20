from netbox_unifi_sync.services.sync.netbox_orm import _Endpoint


class IPRange:
    def __init__(self, **kwargs):
        self.saved = False
        for key, value in kwargs.items():
            setattr(self, key, value)

    def save(self):
        self.saved = True


def test_iprange_endpoint_converts_host_endpoints_to_ipnetwork():
    endpoint = _Endpoint(IPRange)

    translated = endpoint._translate_kwargs({
        "start_address": "10.88.0.50/24",
        "end_address": "10.88.0.200/24",
    })
    assert str(translated["start_address"]) == "10.88.0.50/24"
    assert str(translated["end_address"]) == "10.88.0.200/24"

    created = endpoint.create({
        "start_address": "10.88.0.50/24",
        "end_address": "10.88.0.200/24",
        "description": "UniFi DHCP: LAN",
    })
    assert str(created.start_address) == "10.88.0.50/24"
    assert str(created.end_address) == "10.88.0.200/24"
    assert created.start_address.ip
    assert created.end_address.ip


def test_iprange_endpoint_converts_without_netaddr(monkeypatch):
    real_import = __import__

    def import_without_netaddr(name, *args, **kwargs):
        if name == "netaddr":
            raise ImportError("netaddr unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", import_without_netaddr)

    endpoint = _Endpoint(IPRange)
    translated = endpoint._translate_kwargs({"start_address": "10.88.0.50/24"})

    assert str(translated["start_address"]) == "10.88.0.50/24"
    assert translated["start_address"].ip
