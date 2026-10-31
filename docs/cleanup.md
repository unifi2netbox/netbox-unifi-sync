# NetBox Cleanup Guide

> **Warning**: The cleanup feature **permanently deletes data** from NetBox. There is no undo. Always test in a staging environment first.

---

## Overview

The cleanup phase runs **after** each sync cycle and removes stale/orphaned data from NetBox. It is disabled by default.

## Enabling Cleanup

Enable in plugin `Settings`:

- `cleanup_enabled = true`
- `cleanup_grace_days = 30`

## What Gets Deleted

### 1. Stale Devices

Devices with a serial in the configured NetBox sites/tenant but **not found**
in the current execution's UniFi serial set are candidates. This is broader than
objects proven to have been created by the plugin; review the site/tenant scope.

- The grace period (`cleanup_grace_days`) checks the age of an available, parseable `last_updated` value
- A recent `last_updated` value protects a candidate until the grace period expires; missing/unparseable values do not establish an age
- Device deletion follows NetBox relationship handling; the later orphan-IP pass can delete unassigned tenant IPs
- Default grace period: **30 days**

### 2. Garbage Interfaces

Interfaces with `?` in the name are deleted. These are typically created by API parsing errors or malformed device data.

### 3. Orphan IP Addresses

IP addresses assigned to the tenant but with no `assigned_object` (the interface they were assigned to no longer exists).

### 4. Orphan Cables

Cables where one or both terminations are missing (the connected interface/device was deleted).

### 5. Unused Device Types

Ubiquiti device types with `device_count == 0` are deleted. Before deletion, all device type specs are refreshed from the community + hardcoded database.

---

## Safety Guidelines

### Before Enabling

1. **Test in staging first** — clone your NetBox database and test cleanup there
2. **Review scope** — the grace period applies to stale devices only. Increasing it is not a dry-run and does not protect orphan interfaces, IPs, cables or unused device types.
3. **Review logs** — every deletion is logged at INFO level with the device name and serial
4. **Back up NetBox** — ensure you have a recent database backup

### Recommended Settings

| Scenario | `cleanup_grace_days` | Notes |
|---|---|---|
| Conservative | `90` | 3 months grace period |
| Standard | `30` | 1 month (default) |
| Aggressive | `7` | 1 week |
| Immediate | `0` | No grace period — use with caution |

### What is Never Deleted

The cleanup phase will **never** touch:

- Sites
- Tenants
- Manufacturers
- Device roles
- VRFs
- Prefixes
- VLANs/WLANs
- Custom fields or tags

---

## Monitoring

Watch for these log entries:

```
Cleanup: deleted stale device SW-OLD (AABBCCDDEEFF) from site HQ
Cleanup: deleted 3 garbage interface(s) from site HQ
Cleanup: deleted 2 orphan IP(s)
Cleanup: deleted 1 orphan cable(s) from site HQ
Cleanup: refreshed 42 device type(s), deleted 5 unused device type(s)
```

A second run should report 0 deletions if cleanup was complete.

---

## Disabling Cleanup

Set `cleanup_enabled=false` (default is disabled).

## Authorization, Execution Groups and Limits

Request cleanup using the dashboard checkbox or `--cleanup`. Scheduled runs use
`cleanup_enabled`. Queueing cleanup through the UI/job boundary requires both a
sync permission and `netbox_unifi_sync.run_cleanup`.

Controllers are grouped by credentials and effective site mappings. If multiple
groups are needed, cleanup is skipped for the run so another group's devices
are not mistaken for stale objects. Normal sync continues and the reason is
logged. Inspect `cleanup_requested` and `cleanup_effective` in run details.

The grace period uses `last_updated` as a proxy, not a confirmed offline-since
timestamp. The grace check cannot establish age when the timestamp is absent or
unparseable. Cleanup also includes tenant-wide orphan IPs and manufacturer-wide
unused device types, so it is not restricted to the last device synced.

`--dry-run --cleanup` performs preflight only; it does not list proposed
cleanup deletions. Validate cleanup on a staging database copy and keep a backup.
See the [upgrade guide](upgrade.md) for safe rollout and process-overlap limits.
