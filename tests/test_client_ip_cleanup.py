from types import SimpleNamespace

from netbox_unifi_sync.services import sync_engine


def _device(primary4=None, primary6=None, oob=None):
    return SimpleNamespace(primary_ip4_id=primary4, primary_ip6_id=primary6, oob_ip_id=oob)


def test_primary_ipv4_is_kept():
    assert sync_engine._is_device_identity_ip(SimpleNamespace(pk=10), _device(primary4=10))


def test_primary_ipv6_and_oob_are_kept():
    assert sync_engine._is_device_identity_ip(SimpleNamespace(pk=11), _device(primary6=11))
    assert sync_engine._is_device_identity_ip(SimpleNamespace(pk=12), _device(oob=12))


def test_other_address_is_not_kept():
    assert not sync_engine._is_device_identity_ip(SimpleNamespace(pk=13), _device(primary4=10))


def test_device_without_primary_does_not_match_unsaved_address():
    assert not sync_engine._is_device_identity_ip(SimpleNamespace(pk=None), _device())
    assert not sync_engine._is_device_identity_ip(SimpleNamespace(pk=5), None)
