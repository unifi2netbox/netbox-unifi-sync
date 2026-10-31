"""Release review regressions; Django entry points are loaded without NetBox."""
import ast
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from netbox_unifi_sync.configuration import patched_environ, sanitize_plugin_settings
from netbox_unifi_sync.services import sync_engine, sync_service
from netbox_unifi_sync.services.permissions import can_queue_sync, can_run_cleanup


ROOT = Path(__file__).resolve().parents[1] / 'netbox_unifi_sync'


def _load_function(path, name, namespace, class_name=None):
    """Exercise the real function body while injecting framework dependencies."""
    tree = ast.parse((ROOT / path).read_text())
    nodes = tree.body
    if class_name:
        nodes = next(n for n in nodes if isinstance(n, ast.ClassDef) and n.name == class_name).body
    function = next(n for n in nodes if isinstance(n, ast.FunctionDef) and n.name == name)
    function.decorator_list = []
    module = ast.Module(body=[function], type_ignores=[])
    exec(compile(module, str(ROOT / path), 'exec'), namespace)
    return namespace[name]


def test_dry_run_fails_before_controller_access_when_netbox_is_unavailable(monkeypatch):
    monkeypatch.setattr(sync_service, '_preflight_netbox', lambda settings: {'status': 'error'})
    unifi = Mock()
    monkeypatch.setattr(sync_service, '_preflight_unifi', unifi)
    with pytest.raises(RuntimeError, match='NetBox preflight failed'):
        sync_service._run_preflight({})
    unifi.assert_not_called()


@pytest.mark.parametrize('roles', [
    {'SWITCH': 'Old', 'LAN': 'Canonical'},
    {'LAN': 'Canonical', 'SWITCH': 'Old'},
])
def test_canonical_roles_win_in_either_insertion_order(roles):
    migrate = _load_function('services/orchestrator.py', '_migrate_role_keys', {
        '_ROLE_KEY_ALIASES': {'SWITCH': 'LAN'},
    })
    assert migrate(roles) == ({'LAN': 'Canonical'}, True)


@pytest.mark.parametrize('serial', ['SERIAL2', 'x' * 100, 'Æ' * 100])
def test_serial_suffix_is_deterministic_unique_and_fits_device_name(serial):
    name = sync_engine._device_serial_name('Switch' * 30, serial)
    assert len(name) <= 64
    assert name == sync_engine._device_serial_name('Switch' * 30, serial)
    assert name != sync_engine._device_serial_name('Switch' * 30, serial + '2')


def test_configuration_snapshots_redact_mfa_and_legacy_netbox_credentials():
    snapshot = sanitize_plugin_settings({
        'unifi_mfa_secret': 'private-mfa-value', 'netbox_token': 'private-netbox-value',
    })
    assert snapshot['unifi_mfa_secret'] == '***'
    assert snapshot['netbox_token'] == '***'
    assert 'private-' not in str(snapshot)


def test_overlapping_runtime_contexts_keep_credentials_and_restore_environment(monkeypatch):
    key = 'UNIFI_RUNTIME_REVIEW_KEY'
    monkeypatch.setenv(key, 'original')
    attempted = Event()
    entered = Event()

    def second_run():
        attempted.set()
        with patched_environ({key: 'second'}):
            entered.set()
            assert os.environ[key] == 'second'

    with ThreadPoolExecutor(max_workers=1) as pool:
        with patched_environ({key: 'first'}):
            future = pool.submit(second_run)
            assert attempted.wait(2)
            assert not entered.wait(0.05)
            assert os.environ[key] == 'first'
        future.result(timeout=2)
    assert entered.is_set()
    assert os.environ[key] == 'original'


def test_runtime_context_restores_settings_after_error(monkeypatch):
    key = 'UNIFI_RUNTIME_REVIEW_KEY'
    monkeypatch.delenv(key, raising=False)
    with pytest.raises(ValueError):
        with patched_environ({key: 'temporary'}):
            raise ValueError('failed sync')
    assert key not in os.environ


@pytest.mark.parametrize('permissions, cleanup, allowed', [
    (set(), False, False),
    ({'netbox_unifi_sync.run_cleanup'}, True, False),
    ({'netbox_unifi_sync.run_sync'}, False, True),
    ({'netbox_unifi_sync.add_syncrun'}, False, True),
    ({'netbox_unifi_sync.run_sync'}, True, False),
    ({'netbox_unifi_sync.run_sync', 'netbox_unifi_sync.run_cleanup'}, True, True),
])
def test_enqueue_enforces_sync_and_cleanup_permissions(permissions, cleanup, allowed):
    enqueue = Mock(return_value='queued')
    cls = SimpleNamespace(enqueue=enqueue)
    user = SimpleNamespace(pk=7, has_perm=lambda permission: permission in permissions)
    boundary = _load_function('jobs.py', 'enqueue_sync', {
        'can_queue_sync': can_queue_sync, 'can_run_cleanup': can_run_cleanup,
        'PermissionDenied': PermissionError,
    }, class_name='UnifiSyncJob')
    if allowed:
        assert boundary(cls, user=user, cleanup_requested=cleanup) == 'queued'
        assert enqueue.call_args.kwargs['requested_by_id'] == 7
    else:
        with pytest.raises(PermissionError):
            boundary(cls, user=user, cleanup_requested=cleanup)
        enqueue.assert_not_called()


def test_failed_controller_test_records_attempt_time():
    controller = SimpleNamespace(name='Lab', save=Mock())
    now = object()
    connection_test = Mock(side_effect=RuntimeError('connection failed'))
    view = _load_function('views.py', 'controller_test_view', {
        'HttpRequest': object, 'HttpResponse': object,
        'can_test_controller': lambda user: True,
        'get_object_or_404': lambda *args, **kwargs: controller,
        'UnifiController': object,
        'get_or_create_global_settings': lambda: object(),
        'test_controller_connection': connection_test,
        'timezone': SimpleNamespace(now=lambda: now),
        'sanitize_error': str,
        'messages': SimpleNamespace(error=Mock()),
        'record_event': Mock(),
        'redirect': lambda name: name,
    })
    view(SimpleNamespace(user=object()), 1)
    assert controller.last_tested is now
    assert controller.last_test_status == 'error'
    controller.save.assert_called_once_with(
        update_fields=['last_test_status', 'last_test_error', 'last_tested'],
    )


@pytest.mark.parametrize('same_mapping, expected_groups', [(False, 2), (True, 1)])
def test_controllers_share_execution_only_when_site_mappings_match(same_mapping, expected_groups):
    from collections import defaultdict
    from typing import Any, Iterable
    from netbox_unifi_sync.services._validation import validate_runtime_config

    controllers = [SimpleNamespace(pk=1, name='First'), SimpleNamespace(pk=2, name='Second')]
    settings = SimpleNamespace(enabled=True, tenant_name='Lab', netbox_roles={'LAN': 'Switch'})

    def mappings(rows):
        return {'default': 'Site A' if same_mapping or rows[0].pk == 1 else 'Site B'}

    execute = Mock(return_value={'controllers': 1, 'sites': 1, 'devices': 1})
    run = _load_function('services/orchestrator.py', 'run_sync', {
        'Any': Any, 'Iterable': Iterable, 'defaultdict': defaultdict,
        'get_or_create_global_settings': lambda: settings,
        'get_enabled_controllers': lambda **kwargs: controllers,
        '_runtime_defaults': lambda settings: {},
        'to_controller_runtime': lambda *args: object(),
        'auth_signature': lambda runtime: ('shared-credentials',),
        '_collect_site_mappings': mappings,
        '_validate_runtime_config': validate_runtime_config,
        '_build_override': lambda settings, rows, site_mappings, **kwargs: site_mappings,
        'legacy_execute_sync': execute,
    })
    result = run(dry_run=False, cleanup_requested=True)
    assert execute.call_count == expected_groups
    assert result['details']['cleanup_effective'] is same_mapping
    if not same_mapping:
        assert [call.kwargs['config_overrides'] for call in execute.call_args_list] == [
            {'default': 'Site A'}, {'default': 'Site B'},
        ]
