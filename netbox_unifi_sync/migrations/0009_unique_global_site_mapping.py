from django.db import migrations, models


def reject_duplicate_global_mappings(apps, schema_editor):
    """Protect ambiguous existing mappings from silent deletion during upgrade."""
    SiteMapping = apps.get_model("netbox_unifi_sync", "SiteMapping")
    seen_sites = set()
    duplicate_ids = []
    rows = SiteMapping.objects.filter(controller__isnull=True).order_by("pk")
    for row in rows.iterator():
        if row.unifi_site in seen_sites:
            duplicate_ids.append(row.pk)
        else:
            seen_sites.add(row.unifi_site)
    if duplicate_ids:
        ids = ", ".join(str(pk) for pk in duplicate_ids)
        raise RuntimeError(
            "Duplicate global UniFi site mappings must be resolved before "
            f"applying this migration (duplicate row IDs: {ids})."
        )


class Migration(migrations.Migration):
    dependencies = [("netbox_unifi_sync", "0008_sync_scope_options")]

    operations = [
        migrations.RunPython(
            reject_duplicate_global_mappings,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name="sitemapping",
            constraint=models.UniqueConstraint(
                fields=("unifi_site",),
                condition=models.Q(controller__isnull=True),
                name="unique_global_unifi_site_mapping",
            ),
        ),
    ]
