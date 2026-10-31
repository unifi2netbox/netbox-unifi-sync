from netbox_unifi_sync.services.sync.netbox_orm import _Endpoint, _OrmObject


class IPRange:
    def __init__(self, **kwargs):
        self.saved = False
        for key, value in kwargs.items():
            setattr(self, key, value)

    def save(self):
        self.saved = True


def test_iprange_endpoint_converts_host_endpoints_to_ipnetwork():
    endpoint = _Endpoint(IPRange)

    translated = endpoint._translate_kwargs({
        "start_address": "10.88.0.50/24",
        "end_address": "10.88.0.200/24",
    })
    assert str(translated["start_address"]) == "10.88.0.50/24"
    assert str(translated["end_address"]) == "10.88.0.200/24"

    created = endpoint.create({
        "start_address": "10.88.0.50/24",
        "end_address": "10.88.0.200/24",
        "description": "UniFi DHCP: LAN",
    })
    assert str(created.start_address) == "10.88.0.50/24"
    assert str(created.end_address) == "10.88.0.200/24"
    assert created.start_address.ip
    assert created.end_address.ip


def test_iprange_endpoint_converts_without_netaddr(monkeypatch):
    real_import = __import__

    def import_without_netaddr(name, *args, **kwargs):
        if name == "netaddr":
            raise ImportError("netaddr unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", import_without_netaddr)

    endpoint = _Endpoint(IPRange)
    translated = endpoint._translate_kwargs({"start_address": "10.88.0.50/24"})

    assert str(translated["start_address"]) == "10.88.0.50/24"
    assert translated["start_address"].ip


def test_orm_wrapper_sets_generic_many_to_many_relationships():
    class ManyToManyField:
        many_to_many = True
        many_to_one = False

    class Relation:
        def __init__(self):
            self.values = []

        def set(self, values):
            self.values = list(values)

    relation = Relation()
    instance = type(
        "WirelessLAN",
        (),
        {
            "_meta": type(
                "Meta", (), {"get_field": lambda self, name: ManyToManyField()}
            )(),
            "interfaces": relation,
        },
    )()

    wrapped = _OrmObject(instance)
    wrapped.interfaces = [1, 2]

    assert relation.values == [1, 2]


class _ChangeLoggedDevice:
    """Mimics NetBox's ChangeLoggingMixin: snapshot() records current state."""

    class _meta:
        @staticmethod
        def get_field(name):
            raise LookupError(name)

    def __init__(self):
        self.pk = 1
        self.name = "old"
        self.snapshots = []
        self.saved = []

    def snapshot(self):
        self._prechange_snapshot = {"name": self.name}
        self.snapshots.append(dict(self._prechange_snapshot))

    def save(self, update_fields=None):
        # NetBox's post_save handler compares this snapshot with the new state.
        self.saved.append((self._prechange_snapshot, {"name": self.name}))


def test_snapshot_taken_before_first_change():
    instance = _ChangeLoggedDevice()
    wrapped = _OrmObject(instance)
    wrapped.name = "new"
    wrapped.save()

    assert instance.saved == [({"name": "old"}, {"name": "new"})]


def test_each_save_gets_a_fresh_snapshot():
    instance = _ChangeLoggedDevice()
    wrapped = _OrmObject(instance)
    wrapped.name = "second"
    wrapped.save()
    wrapped.name = "third"
    wrapped.save()

    assert instance.saved == [
        ({"name": "old"}, {"name": "second"}),
        ({"name": "second"}, {"name": "third"}),
    ]


def test_save_without_changes_still_snapshots():
    instance = _ChangeLoggedDevice()
    _OrmObject(instance).save()

    assert instance.saved == [({"name": "old"}, {"name": "old"})]


def _device_with_role_fk():
    class ForeignKey:
        many_to_one = True
        many_to_many = False
        concrete = True
        attname = "role_id"

    class Meta:
        def get_field(self, name):
            # Django's get_field() resolves both the field name and its attname.
            if name in ("role", "role_id"):
                return ForeignKey()
            raise LookupError(name)

    return type("Device", (), {"_meta": Meta(), "role_id": 1})()


def test_setting_fk_attname_with_int_writes_the_column():
    instance = _device_with_role_fk()
    _OrmObject(instance).role_id = 7

    assert instance.role_id == 7
    assert not hasattr(instance, "role_id_id")


def test_setting_fk_name_with_int_writes_the_column():
    instance = _device_with_role_fk()
    _OrmObject(instance).role = 9

    assert instance.role_id == 9


def _ip_with_generic_fk(**field_attrs):
    class GenericForeignKey:
        # GenericForeignKey reports many_to_one but has no DB column.  Before
        # Django 5.1 it is not a Field and has no attname at all; from 5.1 on
        # its attname equals its name.  Either way the PK goes to "<name>_id".
        many_to_one = True
        many_to_many = False
        concrete = False

    for key, value in field_attrs.items():
        setattr(GenericForeignKey, key, value)

    class Meta:
        def get_field(self, name):
            if name == "assigned_object":
                return GenericForeignKey()
            raise LookupError(name)

    return type("IPAddress", (), {"_meta": Meta(), "assigned_object_id": None})()


def test_setting_generic_fk_with_int_writes_object_id_without_attname():
    instance = _ip_with_generic_fk()
    _OrmObject(instance).assigned_object = 3

    assert instance.assigned_object_id == 3


def test_setting_generic_fk_with_int_writes_object_id_with_attname():
    instance = _ip_with_generic_fk(attname="assigned_object")
    _OrmObject(instance).assigned_object = 4

    assert instance.assigned_object_id == 4
    # The GFK descriptor itself must not have been written with the int.
    assert not hasattr(instance, "assigned_object")
