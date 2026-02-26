"""
0006_change_logging

Add ChangeLoggingMixin to GlobalSyncSettings, UnifiController and SiteMapping.

ChangeLoggingMixin contributes two timestamp fields:
  created     — DateTimeField(auto_now_add=True, blank=True, null=True)
  last_updated — DateTimeField(auto_now=True, blank=True, null=True)

GlobalSyncSettings previously had `updated` (auto_now); UnifiController had
`created` (auto_now_add) and `updated` (auto_now).  Both are renamed /
replaced by the mixin fields.  SiteMapping had no timestamps.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_unifi_sync", "0005_feature_parity"),
    ]

    operations = [
        # ── GlobalSyncSettings ─────────────────────────────────────────────
        # Remove old `updated` column; add mixin columns.
        migrations.RemoveField(
            model_name="globalsyncsettings",
            name="updated",
        ),
        migrations.AddField(
            model_name="globalsyncsettings",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="globalsyncsettings",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, null=True, blank=True),
        ),

        # ── UnifiController ────────────────────────────────────────────────
        # Remove old `created` / `updated`; add mixin columns.
        migrations.RemoveField(
            model_name="unificontroller",
            name="created",
        ),
        migrations.RemoveField(
            model_name="unificontroller",
            name="updated",
        ),
        migrations.AddField(
            model_name="unificontroller",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="unificontroller",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, null=True, blank=True),
        ),

        # ── SiteMapping ────────────────────────────────────────────────────
        # No previous timestamps — just add the mixin columns.
        migrations.AddField(
            model_name="sitemapping",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="sitemapping",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, null=True, blank=True),
        ),
    ]
