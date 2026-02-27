from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_unifi_sync", "0006_change_logging"),
    ]

    operations = [
        migrations.AddField(
            model_name="globalsyncsettings",
            name="sync_client_ips",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Sync UniFi client IP addresses to NetBox IPAM. "
                    "IPs are tagged unifi-client and deleted when the client goes offline for > 24 hours."
                ),
            ),
        ),
    ]
