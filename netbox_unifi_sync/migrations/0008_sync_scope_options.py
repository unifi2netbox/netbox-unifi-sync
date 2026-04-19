from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_unifi_sync", "0007_sync_client_ips"),
    ]

    operations = [
        migrations.AddField(
            model_name="globalsyncsettings",
            name="sync_device_custom_fields",
            field=models.BooleanField(
                default=True,
                help_text="Sync UniFi firmware, uptime, MAC, and last-seen values to NetBox custom fields.",
            ),
        ),
        migrations.AddField(
            model_name="globalsyncsettings",
            name="sync_device_status",
            field=models.BooleanField(
                default=False,
                help_text="Update NetBox device status from UniFi online/offline state.",
            ),
        ),
        migrations.AddField(
            model_name="globalsyncsettings",
            name="sync_devices",
            field=models.BooleanField(
                default=True,
                help_text="Create and update UniFi network devices in NetBox DCIM.",
            ),
        ),
        migrations.AddField(
            model_name="globalsyncsettings",
            name="sync_gateway_interfaces",
            field=models.BooleanField(
                default=True,
                help_text="Sync UniFi gateway VLAN/management interfaces and gateway IPs.",
            ),
        ),
        migrations.AddField(
            model_name="globalsyncsettings",
            name="sync_primary_ips",
            field=models.BooleanField(
                default=True,
                help_text="Assign UniFi device management IPs as NetBox primary IPs.",
            ),
        ),
        migrations.AddField(
            model_name="globalsyncsettings",
            name="sync_radio_interfaces",
            field=models.BooleanField(
                default=True,
                help_text="Sync UniFi AP radios as NetBox wireless interfaces.",
            ),
        ),
    ]
