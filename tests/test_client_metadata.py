from main import _client_description


def test_client_description_includes_stable_mac_prefix_and_metadata():
    description = _client_description(
        {
            "mac": "AA:BB:CC:DD:EE:FF",
            "hostname": "iphone-01",
            "ip": "10.0.0.25",
            "ssid": "Corp WiFi",
            "ap_name": "AP-01",
            "signal": -62,
            "last_seen": 1710000000.8,
            "connected_at": "2026-04-19T09:15:00Z",
        }
    )

    assert description == (
        "unifi-client:AA:BB:CC:DD:EE:FF | UniFi client: iphone-01 | "
        "IP: 10.0.0.25 | "
        "SSID: Corp WiFi | AP: AP-01 | Signal: -62dBm | "
        "Last seen: 1710000000 | Connected: 2026-04-19T09:15:00Z"
    )


def test_client_description_omits_empty_metadata():
    assert _client_description(
        {
            "mac": "AA:BB:CC:DD:EE:FF",
            "hostname": "AA:BB:CC:DD:EE:FF",
            "ssid": "",
            "ap_name": None,
            "signal": "",
            "last_seen": None,
        }
    ) == "unifi-client:AA:BB:CC:DD:EE:FF"


def test_client_description_keeps_non_epoch_last_seen_text():
    assert _client_description(
        {
            "mac": "AA:BB:CC:DD:EE:FF",
            "hostname": "camera-01",
            "ip": "192.0.2.10",
            "last_seen": "2026-04-19T10:30:00Z",
        }
    ) == (
        "unifi-client:AA:BB:CC:DD:EE:FF | UniFi client: camera-01 | "
        "IP: 192.0.2.10 | Last seen: 2026-04-19T10:30:00Z"
    )
