from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from netbox_unifi_sync.models import SyncRun, SyncRunStatus


def mark_stale_sync_runs(*, max_age_minutes: int = 120) -> int:
    """Fail pending/running sync rows that are older than any real job should be."""
    cutoff = timezone.now() - timedelta(minutes=max_age_minutes)
    stale_runs = SyncRun.objects.filter(
        status__in=(SyncRunStatus.PENDING, SyncRunStatus.RUNNING),
        started__lt=cutoff,
    )
    count = 0
    for run in stale_runs:
        run.mark_failed(
            f"Marked failed automatically: sync was still {run.status} after "
            f"{max_age_minutes} minutes and no active RQ job was found."
        )
        count += 1
    return count
