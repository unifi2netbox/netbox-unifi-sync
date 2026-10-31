from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import Mock
import time

import pytest

from netbox_unifi_sync.services import sync_engine as engine
from netbox_unifi_sync.services.sync.netbox_orm import _Endpoint


def test_prefix_sync_disabled_never_creates(monkeypatch):
    monkeypatch.setenv('SYNC_PREFIXES', 'false')
    nb = Mock()
    assert engine.ensure_prefix_for_ip(nb, Mock(), Mock(), None, '10.50.0.1') is None
    engine.sync_site_prefixes(nb, Mock(), Mock(), Mock())
    nb.ipam.prefixes.create.assert_not_called()


def test_parallel_prefix_creation_is_idempotent(monkeypatch):
    monkeypatch.setenv('SYNC_PREFIXES', 'true')
    monkeypatch.setattr(engine, '_infer_prefix_from_unifi_network_cache', lambda ip: '10.50.0.0/24')
    records = []
    def create(payload):
        time.sleep(0.01)
        record = SimpleNamespace(id=1, **payload)
        records.append(record)
        return record
    endpoint = Mock()
    endpoint.get.side_effect = lambda **kw: records[0] if records else None
    endpoint.create.side_effect = create
    nb = SimpleNamespace(ipam=SimpleNamespace(prefixes=endpoint))
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: engine.ensure_prefix_for_ip(
            nb, SimpleNamespace(id=1, name='Lab'), None, None, '10.50.0.1'), range(8)))
    assert len(records) == 1
    assert all(result is records[0] for result in results)


def test_dtl_part_number_variants_reuse_imported_type(monkeypatch):
    spec = {'part_number': 'USW-48-POE', 'model_name': 'Ubiquiti UniFi Switch 48 PoE Gen2'}
    monkeypatch.setattr(engine, '_community_specs', {'by_part': {'USW-48-POE': spec}, 'by_model': {}})
    imported = SimpleNamespace(id=42, part_number="USW-48-POE", model=spec["model_name"])
    endpoint = Mock()
    endpoint.filter.return_value = [imported]
    nb = SimpleNamespace(dcim=SimpleNamespace(device_types=endpoint))
    for model in ('USW 48 POE', 'USW-48-POE'):
        specs = engine._resolve_device_specs(model)
        assert specs == spec
        assert engine.find_device_type(nb, SimpleNamespace(id=1), model) == (imported, True)
    endpoint.create.assert_not_called()


@pytest.mark.parametrize('message', [
    'Device name must be unique per site',
    'ORM create failed for Device: duplicate key value violates unique constraint "dcim_device_unique_name_site_tenant"',
])
def test_device_name_conflicts_recognized(message):
    assert engine._is_device_name_conflict(RuntimeError(message))
    assert not engine._is_device_name_conflict(RuntimeError('duplicate serial'))


def test_counter_signals_are_not_overwritten_by_later_saves():
    class CounterCacheField:
        name = 'power_port_count'
    class Device:
        _meta = SimpleNamespace(concrete_fields=[CounterCacheField()])
        pk = None
        power_port_count = 0
        stored_count = 0
        def __init__(self, **kw):
            self.__dict__.update(kw)
        def save(self):
            if self.pk is None:
                self.pk = 1
                self.stored_count = 2  # Component post_save updates the database.
            else:
                self.stored_count = self.power_port_count
        def refresh_from_db(self, fields):
            assert fields == ['power_port_count']
            self.power_port_count = self.stored_count
    device = _Endpoint(Device).create({})
    assert device.power_port_count == 2
    raw = object.__getattribute__(device, '_instance')
    raw.stored_count = 3  # Another component was added after creation.
    device.name = 'renamed'
    device.save()
    assert raw.stored_count == 3
    assert device.name == 'renamed'


@pytest.mark.parametrize('parent_prefix, expected_mask', [(None, 32), ('10.50.0.0/24', 24)])
def test_duplicate_device_names_create_rename_and_repeat_sync(monkeypatch, parent_prefix, expected_mask):
    from copy import deepcopy
    role = SimpleNamespace(id=1, name='Switch')
    dtype = SimpleNamespace(id=2)
    records = []
    persisted = {}
    class Device:
        def __init__(self, payload):
            self.__dict__.update(payload)
            self.id = len(records) + 1
            self.device_type = dtype
            self.role = role
            self.tags = []
            self.asset_tag = None
        def save(self):
            for other in records:
                if other.id != self.id and persisted[other.id].lower() == self.name.lower():
                    raise RuntimeError('duplicate key violates "dcim_device_unique_name_site_tenant"')
            persisted[self.id] = self.name
    endpoint = Mock()
    endpoint.get.side_effect = lambda **kw: next((d for d in records if d.serial == kw['serial']), None)
    def create(payload):
        if payload['name'].lower() in [n.lower() for n in persisted.values()]:
            raise RuntimeError('ORM create failed for Device: dcim_device_unique_name_site_tenant')
        device = Device(deepcopy(payload))
        records.append(device)
        persisted[device.id] = device.name
        return device
    endpoint.create.side_effect = create
    nb = SimpleNamespace(dcim=SimpleNamespace(devices=endpoint))
    monkeypatch.setattr(engine, 'select_netbox_role_for_device', lambda d: (role, 'SWITCH'))
    monkeypatch.setattr(engine, 'get_vrf_for_site', lambda *a: (None, None))
    monkeypatch.setattr(engine, '_resolve_device_specs', lambda m: None)
    monkeypatch.setattr(engine, 'find_device_type', lambda *a: (dtype, False))
    monkeypatch.setattr(engine, 'ensure_device_type_specs', Mock())
    monkeypatch.setattr(engine, 'get_postable_fields', lambda *a: {'role': True})
    monkeypatch.setattr(engine, 'ensure_tag', lambda *a: None)
    monkeypatch.setattr(engine, 'sync_device_interfaces', Mock())
    monkeypatch.setenv('SYNC_DEVICE_CUSTOM_FIELDS', 'false')
    monkeypatch.setenv('SYNC_PRIMARY_IPS', 'false')
    def sync(serial, name='USW Lite 8 PoE'):
        engine.process_device(Mock(), nb, SimpleNamespace(id=3, name='Lab'),
                              {'name': name, 'serial': serial, 'model': 'USW-Lite-8-PoE'},
                              SimpleNamespace(id=1), SimpleNamespace(id=1))
    sync('SERIAL1')
    sync('SERIAL2')
    assert list(persisted.values()) == ['USW Lite 8 PoE', 'USW Lite 8 PoE_SERIAL2']
    sync('SERIAL1')
    sync('SERIAL2')
    assert len(records) == 2
    assert list(persisted.values()) == ['USW Lite 8 PoE', 'USW Lite 8 PoE_SERIAL2']
    sync('SERIAL3', 'Another name')
    sync('SERIAL3')
    assert persisted[3] == 'USW Lite 8 PoE_SERIAL3'

    # Prefix sync off must still allow primary IP assignment with a host mask.
    monkeypatch.setenv('SYNC_PRIMARY_IPS', 'true')
    monkeypatch.setenv('SYNC_PREFIXES', 'false')
    monkeypatch.setattr(engine, 'is_ip_in_dhcp_range', lambda ip: False)
    nb.ipam = SimpleNamespace(prefixes=Mock(), ip_addresses=Mock())
    nb.ipam.prefixes.filter.return_value = (
        [SimpleNamespace(prefix=parent_prefix)] if parent_prefix else []
    )
    nb.ipam.ip_addresses.get.return_value = None
    nb.ipam.ip_addresses.create.return_value = SimpleNamespace(
        id=99, assigned_object_id=10, assigned_object_type='dcim.interface')
    nb.dcim.interfaces = Mock()
    nb.dcim.interfaces.get.return_value = SimpleNamespace(id=10)
    records[0].primary_ip4 = None
    engine.process_device(Mock(), nb, SimpleNamespace(id=3, name='Lab'),
                          {'name': 'USW Lite 8 PoE', 'serial': 'SERIAL1',
                           'model': 'USW-Lite-8-PoE', 'ip': '10.50.0.10'},
                          SimpleNamespace(id=1), SimpleNamespace(id=1))
    nb.ipam.prefixes.create.assert_not_called()
    assert nb.ipam.ip_addresses.create.call_args.args[0]['address'] == f'10.50.0.10/{expected_mask}'
    assert records[0].primary_ip4 == 99


def test_device_name_conflict_uses_wrapped_database_constraint():
    database_error = RuntimeError('localized database error')
    database_error.diag = SimpleNamespace(constraint_name='dcim_device_unique_name_site_tenant')
    wrapped = RuntimeError('ORM create failed')
    wrapped.__cause__ = database_error
    assert engine._is_device_name_conflict(wrapped)
