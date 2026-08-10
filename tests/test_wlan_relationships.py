from types import SimpleNamespace

from netbox_unifi_sync.services.sync_engine import (
    _wlan_broadcast_device_ids,
    _wlan_vlan_id,
    sync_site_wlans,
)


class Endpoint:
    def __init__(self, *, get=None, filtered=None, created=None):
        self.get_result = get
        self.filtered = filtered or []
        self.created = created
        self.created_payload = None

    def get(self, **kwargs):
        if callable(self.get_result):
            return self.get_result(kwargs)
        return self.get_result

    def filter(self, **kwargs):
        return list(self.filtered)

    def create(self, payload):
        self.created_payload = payload
        return self.created or SimpleNamespace(id=999)


class RelatedObjects:
    def __init__(self, *ids):
        self.items = [SimpleNamespace(id=value) for value in ids]

    def all(self):
        return list(self.items)


def _client(existing_wlans=None):
    vlan = SimpleNamespace(id=1000, vid=100)
    vlan_group = SimpleNamespace(id=10)
    nb_device = SimpleNamespace(id=20)
    radio_interfaces = [
        SimpleNamespace(id=501, type="ieee802.11ax"),
        SimpleNamespace(id=502, type="ieee802.11ac"),
        SimpleNamespace(id=503, type="1000base-t"),
    ]
    wireless_lans = Endpoint(filtered=existing_wlans or [])
    return SimpleNamespace(
        ipam=SimpleNamespace(
            vlan_groups=Endpoint(get=vlan_group),
            vlans=Endpoint(get=vlan),
        ),
        dcim=SimpleNamespace(
            devices=Endpoint(get=nb_device),
            interfaces=Endpoint(filtered=radio_interfaces),
        ),
        wireless=SimpleNamespace(
            wireless_lan_groups=Endpoint(get=SimpleNamespace(id=30)),
            wireless_lans=wireless_lans,
        ),
    )


def _site(wlan):
    return SimpleNamespace(
        wlan_conf=SimpleNamespace(all=lambda: [wlan]),
    )


def test_integration_wlan_relationship_values_are_normalized():
    wlan = {
        "network": {"type": "VLAN", "vlanId": 100},
        "broadcastingDeviceIds": ["ap-1", {"id": "ap-2"}],
    }

    assert _wlan_vlan_id(wlan) == 100
    assert _wlan_broadcast_device_ids(wlan) == {"ap-1", "ap-2"}


def test_new_wlan_payload_links_site_vlan_and_broadcasting_ap_radios():
    wlan = {
        "name": "Corporate",
        "enabled": True,
        "securityConfiguration": {"type": "WPA2_PERSONAL"},
        "network": {"vlanId": 100},
        "broadcastingDeviceIds": ["ap-1"],
    }
    nb = _client()

    sync_site_wlans(
        nb,
        _site(wlan),
        SimpleNamespace(id=1, name="HQ"),
        SimpleNamespace(id=2),
        devices=[{"id": "ap-1", "macAddress": "aa:bb:cc:dd:ee:ff"}],
    )

    payload = nb.wireless.wireless_lans.created_payload
    assert payload["ssid"] == "Corporate"
    assert payload["vlan"] == 1000
    assert payload["interfaces"] == [501, 502]


def test_missing_broadcast_metadata_does_not_clear_existing_interfaces():
    existing = SimpleNamespace(
        status="active",
        auth_type="wpa-personal",
        vlan=SimpleNamespace(id=1000),
        interfaces=RelatedObjects(501),
        save=lambda: (_ for _ in ()).throw(AssertionError("unexpected save")),
    )
    nb = _client(existing_wlans=[existing])
    wlan = {
        "name": "Corporate",
        "enabled": True,
        "securityConfiguration": {"type": "WPA2_PERSONAL"},
        "network": {"vlanId": 100},
    }

    sync_site_wlans(
        nb,
        _site(wlan),
        SimpleNamespace(id=1, name="HQ"),
        SimpleNamespace(id=2),
        devices=[],
    )

    assert [item.id for item in existing.interfaces.all()] == [501]


def test_unavailable_device_inventory_does_not_clear_existing_interfaces():
    existing = SimpleNamespace(
        status="active",
        auth_type="wpa-personal",
        vlan=SimpleNamespace(id=1000),
        interfaces=RelatedObjects(501),
        save=lambda: (_ for _ in ()).throw(AssertionError("unexpected save")),
    )
    nb = _client(existing_wlans=[existing])
    wlan = {
        "name": "Corporate",
        "enabled": True,
        "securityConfiguration": {"type": "WPA2_PERSONAL"},
        "network": {"vlanId": 100},
        "broadcastingDeviceIds": ["ap-1"],
    }

    sync_site_wlans(
        nb,
        _site(wlan),
        SimpleNamespace(id=1, name="HQ"),
        SimpleNamespace(id=2),
        devices=None,
    )

    assert [item.id for item in existing.interfaces.all()] == [501]
