from main import normalize_port_data


def test_normalize_integration_port_enriches_description_with_profile_vlan_and_poe():
    ports = normalize_port_data(
        {
            "interfaces": {
                "ports": [
                    {
                        "name": "Port 1",
                        "maxSpeed": 2500,
                        "enabled": True,
                        "poeMode": "auto",
                        "poePower": 6400,
                        "portProfileName": "AP Trunk",
                        "nativeVlan": 10,
                        "taggedVlanIds": [20, 30],
                        "isUplink": True,
                    }
                ]
            }
        },
        api_style="integration",
    )

    assert ports == [
        {
            "name": "Port 1",
            "type": "2.5gbase-t",
            "speed_kbps": 2500000,
            "enabled": True,
            "poe_mode": "pse",
            "mac_address": None,
            "is_uplink": True,
            "description": (
                "Uplink | Profile: AP Trunk | Native VLAN: 10 | "
                "Tagged VLANs: 20, 30 | PoE: auto | PoE draw: 6.4W | "
                "Max speed: 2500Mbps"
            ),
        }
    ]


def test_normalize_legacy_port_enriches_description_from_portconf_and_vlans():
    ports = normalize_port_data(
        {
            "port_table": [
                {
                    "name": "Port 2",
                    "speed": 1000,
                    "up": True,
                    "poe_mode": "off",
                    "portconf_name": "Client Access",
                    "vlan": 40,
                    "tagged_vlans": "50,60",
                    "mac": "aa:bb:cc:dd:ee:ff",
                }
            ]
        },
        api_style="legacy",
    )

    assert ports[0]["description"] == (
        "Profile: Client Access | Native VLAN: 40 | Tagged VLANs: 50, 60 | "
        "PoE: off | Max speed: 1000Mbps"
    )
    assert ports[0]["mac_address"] == "aa:bb:cc:dd:ee:ff"
