from main import _client_description


def test_client_description_includes_stable_mac_prefix_and_metadata():
    description = _client_description(
        {
            "mac": "AA:BB:CC:DD:EE:FF",
            "hostname": "iphone-01",
            "ssid": "Corp WiFi",
            "ap_name": "AP-01",
            "signal": -62,
            "last_seen": 1710000000.8,
        }
    )

    assert description == (
        "unifi-client:AA:BB:CC:DD:EE:FF | Host: iphone-01 | "
        "SSID: Corp WiFi | AP: AP-01 | Signal: -62dBm | "
        "Last seen: 1710000000"
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
