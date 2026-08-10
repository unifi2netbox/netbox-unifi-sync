"""Authorization helpers shared by UI and job-enqueue boundaries."""

from __future__ import annotations


def can_queue_sync(user) -> bool:
    return bool(
        user
        and (
            user.has_perm("netbox_unifi_sync.run_sync")
            or user.has_perm("netbox_unifi_sync.add_syncrun")
        )
    )


def can_run_cleanup(user) -> bool:
    return bool(user and user.has_perm("netbox_unifi_sync.run_cleanup"))


def can_test_controller(user) -> bool:
    return bool(
        user
        and (
            user.has_perm("netbox_unifi_sync.test_controller")
            or user.has_perm("netbox_unifi_sync.change_unificontroller")
        )
    )
