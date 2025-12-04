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

---

## Linting Status

- **Black**: All 897 files pass formatting check ✓
- **flake8**: Modified files pass linting ✓
  - Note: Pre-existing lint error in third-party file `awx/ui/src/node_modules/flatted/python/flatted.py` (unrelated to upgrade)

---

## Next Steps (Pending)

1. ~~Run linting tests~~ ✓ (modified files pass)
2. Run unit tests
3. Run migration tests
4. Run collection tests
5. Address any test failures
