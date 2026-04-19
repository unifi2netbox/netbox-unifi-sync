from types import SimpleNamespace

from netbox_unifi_sync.services.sync.ipam import set_unifi_device_static_ip


class FakeUnifi:
    api_style = "integration"

    def __init__(self):
        self.calls = []

    def make_request(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return {"meta": {"rc": "ok"}}


def test_static_ip_writeback_skips_integration_api():
    unifi = FakeUnifi()

    result = set_unifi_device_static_ip(
        unifi,
        SimpleNamespace(api_id="site-id", name="Default"),
        {"id": "device-id"},
        "192.0.2.10",
    )

    assert result is False
    assert unifi.calls == []
