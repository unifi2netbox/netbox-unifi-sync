from types import SimpleNamespace

from netbox_unifi_sync.services.sync import ipam


def _reset_ipam_state():
    ipam._assigned_static_ips.clear()
    ipam._exhausted_static_prefixes.clear()
    ipam._unifi_dhcp_ranges.clear()
    with ipam._static_prefix_locks_lock:
        ipam._static_prefix_locks.clear()


def test_exhausted_prefix_is_cached_within_run(monkeypatch):
    _reset_ipam_state()

    prefix = SimpleNamespace(id=10, prefix="10.0.0.0/24")
    tenant = SimpleNamespace(id=1)

    ipam._unifi_dhcp_ranges["site-a"] = [ipam.ipaddress.ip_network("10.0.0.0/24")]

    calls = {"count": 0}

    def fake_fetch(network_str):
        calls["count"] += 1
        return [f"10.0.0.{i}" for i in range(2, 52)]

    monkeypatch.setattr(ipam, "_fetch_assigned_ips_for_network", fake_fetch)
    monkeypatch.setattr(ipam, "ping_ip", lambda _: False)

    first = ipam.find_available_static_ip(None, prefix, None, tenant, unifi_device_ips=set())
    second = ipam.find_available_static_ip(None, prefix, None, tenant, unifi_device_ips=set())

    assert first is None
    assert second is None
    assert calls["count"] == 1


def test_finds_available_candidate_when_not_filtered(monkeypatch):
    _reset_ipam_state()

    prefix = SimpleNamespace(id=20, prefix="192.168.10.0/24")
    tenant = SimpleNamespace(id=1)

    def fake_fetch(network_str):
        # .1 through .9 are already assigned in NetBox;
        # .10 will be skipped via unifi_device_ips, leaving .11 as first candidate
        return [f"192.168.10.{i}" for i in range(1, 10)]

    monkeypatch.setattr(ipam, "_fetch_assigned_ips_for_network", fake_fetch)
    monkeypatch.setattr(ipam, "ping_ip", lambda _: False)

    result = ipam.find_available_static_ip(
        None,
        prefix,
        None,
        tenant,
        unifi_device_ips={"192.168.10.10"},
    )

    assert result == "192.168.10.11/24"
