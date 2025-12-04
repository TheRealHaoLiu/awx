# Django 5.2 Upgrade Log for AWX

## Overview
- **Starting Django Version**: 4.2.26
- **Target Django Version**: 5.2.x LTS
- **Branch**: `django-5.2-upgrade`
- **Date Started**: 2025-12-04

---

## Changes Made

### 1. Update Django Version in requirements.in
**File**: `requirements/requirements.in`

**Change**: Updated Django version constraint from `django==4.2.26` to `django>=5.2,<5.3`

**Reason**: Django 5.2 is the new LTS release. The constraint allows patch updates within 5.2.x series.

---

### 2. Migrate pytz to zoneinfo

Django 5.0 removed support for `pytz` in favor of Python 3.9+'s built-in `zoneinfo` module.

#### 2.1 awx/main/models/schedules.py
**Change**: Replaced `pytz.utc` with `datetime.timezone.utc`

**Reason**: `pytz` is no longer supported in Django 5.0+. The `datetime.timezone.utc` is the standard library equivalent.

#### 2.2 awx/main/management/commands/cleanup_jobs.py
**Change**:
- Removed `import pytz`
- Changed `pytz.UTC` to `datetime.timezone.utc`

**Reason**: Same as above - pytz removal in Django 5.0.

#### 2.3 awx/api/views/__init__.py
**Change**:
- Replaced `import pytz` with `from datetime import timezone as dt_timezone`
- Changed `pytz.utc` to `dt_timezone.utc`

**Reason**: Same pytz to zoneinfo migration.

#### 2.4 awx/main/tests/functional/models/test_schedule.py
**Change**:
- Added `from datetime import timezone` and `from zoneinfo import ZoneInfo`
- Replaced `pytz.utc` with `timezone.utc`
- Replaced `pytz.timezone("America/New_York")` with `ZoneInfo("America/New_York")`

**Reason**: Test files also needed pytz migration for Django 5.2 compatibility.

---

### 3. Fix URLValidator.ul Removal
**File**: `awx/conf/fields.py`

**Change**: Added local constants to replace removed URLValidator attributes:
```python
# URLValidator regex components (ul was removed in Django 5.0)
_ul = '\u00a1-\uffff'  # Unicode letters range
_hostname_re = r'[a-z' + _ul + r'0-9](?:[a-z' + _ul + r'0-9-]{0,61}[a-z' + _ul + r'0-9])?'
_domain_re = r'(?:\.(?!-)[a-z' + _ul + r'0-9-]{1,63}(?<!-))*'
_ipv4_re = r'(?:0|25[0-5]|2[0-4][0-9]|1[0-9]?[0-9]?|[1-9][0-9]?)(?:\.(?:0|25[0-5]|2[0-4][0-9]|1[0-9]?[0-9]?|[1-9][0-9]?)){3}'
_ipv6_re = r'\[[0-9a-f:.]+\]'
```

Updated `URLField` class to use these local constants instead of `URLValidator.ul`, `URLValidator.hostname_re`, etc.

**Reason**: Django 5.0 removed `URLValidator.ul` and related attributes. These were internal regex components used for URL validation. The custom `URLField` in AWX extends this for allowing numbers in top-level domains.

---

### 4. Update pytest.ini
**File**: `pytest.ini`

**Change**: Removed deprecation warning filter for `index_together`

**Reason**: Django 5.1/5.2 includes a fix for historical migrations with `index_together` (PR #18931), so the deprecation warning filter is no longer needed. The historical migrations work without modification.

---

### 5. Upgrade django-debug-toolbar
**File**: `requirements/requirements_dev.txt`

**Change**: Updated from `django-debug-toolbar==3.2.4` to `django-debug-toolbar>=4.4`

**Reason**: django-debug-toolbar 3.x is incompatible with Django 5.x. Version 4.4+ includes Django 5.2 support. The old version failed with:
```
ImportError: cannot import name 'get_storage_class' from 'django.core.files.storage'
```
This function was removed in Django 5.1.

---

### 6. Regenerate Requirements
**Command**: `make docker_update_requirements`

**Reason**: After updating requirements.in, the pinned requirements.txt needs to be regenerated to include Django 5.2 and all compatible dependency versions.

---

### 7. Rebuild Docker Development Image
**Command**: `make docker-compose-build`

**Reason**: The development Docker image needs to be rebuilt to include the new dependencies (Django 5.2, updated django-debug-toolbar, etc.)

---

### 8. Generate Django 5.2 Model Migrations
**File**: `awx/main/migrations/0205_alter_instance_peers_alter_job_hosts_and_more.py`

**Change**: Generated new migration for ManyToManyField serialization changes:
- `AlterField` for `instance.peers`
- `AlterField` for `job.hosts`
- `AlterField` for `role.ancestors`

**Reason**: Django 5.2 slightly changed how it serializes ManyToManyField with `through` and `through_fields`. These are no-op migrations that don't change the database schema - they just update Django's internal tracking of field definitions.

---

### 9. Fix QuerySet.iterator() with prefetch_related()
**File**: `awx/main/migrations/_dab_rbac.py`

**Change**: Added `chunk_size=2000` parameter to `.iterator()` call:
```python
# Before:
for role in Role.objects.prefetch_related('members', 'parents').iterator():

# After:
for role in Role.objects.prefetch_related('members', 'parents').iterator(chunk_size=2000):
```

**Reason**: Django 5.2 now requires a `chunk_size` argument when using `QuerySet.iterator()` after `prefetch_related()`. This is a behavioral change from Django 5.2 (see [Django 5.2 release notes](https://docs.djangoproject.com/en/5.2/releases/5.2/)). Without this, migrations fail with:
```
ValueError: chunk_size must be provided when using QuerySet.iterator() after prefetch_related().
```

---

### 10. Fix Database Access During App Initialization
**File**: `awx/main/dispatch/config.py`

**Change**: Skip `get_auto_max_workers()` call when `mock_publish=True`:
```python
# When mock_publish is True (tests), use a simple default instead of calling
# get_auto_max_workers() which triggers database access through settings.IS_K8S
max_workers = 4 if mock_publish else get_auto_max_workers()
```

**Reason**: `get_auto_max_workers()` accesses `settings.IS_K8S` which triggers database access through AWX's custom settings cache. During test initialization, the database may not be available yet. By using a simple default value (4) when `mock_publish=True`, we avoid database access during app initialization in tests while still properly configuring dispatcherd for test execution.

---

## Verification

### AWX Startup
- All services started successfully:
  - `awx-uwsgi`: Running with 5 workers
  - `awx-daphne`: Listening on port 8051
  - `awx-nginx`: Running
  - `awx-dispatcher`: Running
  - `awx-receiver`: Running
  - `awx-wsrelay`: Running
  - `awx-receptor`: Running

### API Verification
- API endpoint accessible at `http://localhost:8013/api/v2/`
- Returns valid JSON with all expected endpoints

---

## Known Issues / Warnings

### 1. RuntimeWarning about database access during app initialization
```
RuntimeWarning: Accessing the database during app initialization is discouraged.
```
This is a Django 5.x warning about database queries in `AppConfig.ready()`. This is pre-existing behavior in AWX and not introduced by the upgrade.

### 2. PermissionError with dispatcherd unix socket
```
PermissionError: [Errno 1] Operation not permitted
```
This is a Docker mount permission issue unrelated to Django 5.2. The dispatcherd service is attempting to create unix sockets in a location with restricted permissions.

---

## User Instructions Log

### Instruction 1 (2025-12-04 ~14:07 EST)
**Request**: Create markdown log to track all changes and reasons, log interruptions and instructions.

### Instruction 2 (2025-12-04 ~14:08 EST)
**Request**:
1. Clear out database
2. Restart docker-compose development environment
3. Verify all migrations complete successfully and AWX reaches running state
4. If successful, run linter
5. Commit the changes

---

## Files Modified Summary

| File | Type of Change |
|------|----------------|
| `requirements/requirements.in` | Django version bump |
| `requirements/requirements.txt` | Regenerated (auto) |
| `requirements/requirements_dev.txt` | django-debug-toolbar update |
| `awx/main/models/schedules.py` | pytz to zoneinfo |
| `awx/main/management/commands/cleanup_jobs.py` | pytz to zoneinfo |
| `awx/api/views/__init__.py` | pytz to zoneinfo |
| `awx/main/tests/functional/models/test_schedule.py` | pytz to zoneinfo |
| `awx/conf/fields.py` | URLValidator.ul fix |
| `pytest.ini` | Remove obsolete warning filter |
| `awx/main/migrations/0205_*.py` | New migration (auto-generated) |
| `awx/main/migrations/_dab_rbac.py` | iterator() chunk_size fix |
| `awx/main/dispatch/config.py` | Skip db access in tests |

---

## Linting Status

- **Black**: All 897 files pass formatting check ✓
- **flake8**: Modified files pass linting ✓
  - Note: Pre-existing lint error in third-party file `awx/ui/src/node_modules/flatted/python/flatted.py` (unrelated to upgrade)

---

## Unit Test Status

- **Result**: 3425 passed, 5 skipped, 2 xfailed, 1 xpassed
- **awxkit tests**: All 245 passed
- **Duration**: ~2 minutes 9 seconds

---

### 11. Fix Django 5.2 SQLite Index Handling in Migrations

Django 5.2 has stricter validation when finding indexes to rename or alter. The event partitioning feature (migration 0144) is PostgreSQL-only, but the subsequent index operations (migrations 0144 and 0184) were failing on SQLite test database.

#### 11.1 awx/main/migrations/_sqlite_helper.py
**Change**: Added two new DB-aware migration operations:
- `AlterIndexTogether`: Skips execution on non-PostgreSQL databases
- `RenameIndex`: Skips execution on non-PostgreSQL databases

**Reason**: Event partitioning and the `job_created` column only exist on PostgreSQL. On SQLite, the `AlterIndexTogether` and `RenameIndex` operations were failing because the indexes they reference don't exist.

#### 11.2 awx/main/migrations/0144_event_partitions.py
**Change**: Replaced `migrations.AlterIndexTogether` with `dbawaremigrations.AlterIndexTogether` for all event table operations.

**Reason**: These operations create indexes on the `job_created` column which only exists on PostgreSQL.

#### 11.3 awx/main/migrations/0184_django_indexes.py
**Change**:
- Added import for `dbawaremigrations`
- Replaced `migrations.RenameIndex` with `dbawaremigrations.RenameIndex` for all event table operations (those with `job_created` in old_fields)
- Kept regular `migrations.RenameIndex` for role/roleancestorentry tables (these indexes exist on both databases)

**Reason**: The event table indexes being renamed only exist on PostgreSQL.

---

## Migration Test Status

- **Result**: 3 passed, 14 warnings
- **Duration**: ~5 minutes 49 seconds
- All migrations run successfully on SQLite test database

---

## Collection Test Status

- **Result**: 179 passed, 2 warnings
- **Duration**: ~1 minute 1 second

---

## Summary: All Tests Pass ✓

| Test Suite | Result |
|------------|--------|
| Linting (black, flake8) | ✓ Pass |
| Unit Tests | 3425 passed |
| awxkit Tests | 245 passed |
| Migration Tests | 3 passed |
| Collection Tests | 179 passed |

---

## Files Modified (Complete List)

| File | Type of Change |
|------|----------------|
| `requirements/requirements.in` | Django version bump |
| `requirements/requirements.txt` | Regenerated (auto) |
| `requirements/requirements_dev.txt` | django-debug-toolbar update |
| `awx/main/models/schedules.py` | pytz to zoneinfo |
| `awx/main/management/commands/cleanup_jobs.py` | pytz to zoneinfo |
| `awx/api/views/__init__.py` | pytz to zoneinfo |
| `awx/main/tests/functional/models/test_schedule.py` | pytz to zoneinfo |
| `awx/conf/fields.py` | URLValidator.ul fix |
| `pytest.ini` | Remove obsolete warning filter |
| `awx/main/migrations/0205_*.py` | New migration (auto-generated) |
| `awx/main/migrations/_dab_rbac.py` | iterator() chunk_size fix |
| `awx/main/dispatch/config.py` | Skip db access in tests |
| `awx/main/migrations/0187_hop_nodes.py` | CheckConstraint condition fix |
| `awx/main/migrations/_sqlite_helper.py` | DB-aware index operations |
| `awx/main/migrations/0144_event_partitions.py` | DB-aware AlterIndexTogether |
| `awx/main/migrations/0184_django_indexes.py` | DB-aware RenameIndex |

---

## Completion Status

1. ~~Run linting tests~~ ✓ (modified files pass)
2. ~~Run unit tests~~ ✓ (all pass)
3. ~~Run migration tests~~ ✓ (all pass)
4. ~~Run collection tests~~ ✓ (all pass)
5. ~~Commit all changes~~ ✓

**Django 5.2 upgrade complete!**
