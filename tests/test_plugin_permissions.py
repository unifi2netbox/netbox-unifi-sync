from netbox_unifi_sync.services.permissions import (
    can_queue_sync,
    can_run_cleanup,
    can_test_controller,
)


class UserWithPermissions:
    def __init__(self, *permissions):
        self.permissions = set(permissions)

    def has_perm(self, permission):
        return permission in self.permissions


def test_sync_permission_supports_custom_and_standard_permissions():
    assert can_queue_sync(UserWithPermissions("netbox_unifi_sync.run_sync"))
    assert can_queue_sync(UserWithPermissions("netbox_unifi_sync.add_syncrun"))
    assert not can_queue_sync(UserWithPermissions())
    assert not can_queue_sync(None)


def test_cleanup_requires_its_dedicated_permission():
    run_only = UserWithPermissions("netbox_unifi_sync.run_sync")
    cleanup = UserWithPermissions("netbox_unifi_sync.run_cleanup")

    assert not can_run_cleanup(run_only)
    assert can_run_cleanup(cleanup)
    assert not can_run_cleanup(None)


def test_controller_test_supports_custom_and_change_permissions():
    assert can_test_controller(
        UserWithPermissions("netbox_unifi_sync.test_controller")
    )
    assert can_test_controller(
        UserWithPermissions("netbox_unifi_sync.change_unificontroller")
    )
    assert not can_test_controller(UserWithPermissions())
