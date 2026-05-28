# Move FinancialYear from `sfm` to `ibms`

## Background

The `FinancialYear` model was originally defined in the `sfm` app but is used as a foreign key
by almost every model in the `ibms` app. As part of the planned future removal of the `sfm` app,
`FinancialYear` has been relocated to the `ibms` app where the majority of its references live.

---

## Approach

Django's `SeparateDatabaseAndState` was used throughout to transfer model ownership without
touching the database until the final table-rename step. This makes the migration safe to apply
in production with no data loss and no downtime risk beyond the brief table rename.

---

## Migration sequence

The migrations must be applied in dependency order. Django resolves this automatically.

| Migration | App | Type | DB change? | Purpose |
|-----------|-----|------|-----------|---------|
| `0027_add_financialyear` | `ibms` | `SeparateDatabaseAndState` | ✗ | Registers `ibms.FinancialYear` in the migration state, pointing at the existing `sfm_financialyear` table via `Meta.db_table` |
| `0010_remove_financialyear` | `sfm` | `SeparateDatabaseAndState` | ✗ | Removes `sfm.FinancialYear` from the migration state (ibms must own it first) |
| `0028_retarget_financialyear_fks` | `ibms` | `SeparateDatabaseAndState` | ✗ | Retargets all 12 ibms FK fields from `sfm.FinancialYear` → `ibms.FinancialYear` in the migration state |
| `0011_retarget_financialyear_fks` | `sfm` | `SeparateDatabaseAndState` | ✗ | Retargets `SFMMetric.fy` and `Quarter.fy` from `sfm.FinancialYear` → `ibms.FinancialYear` in the migration state |
| `0029_rename_financialyear_table` | `ibms` | `AlterModelTable` | ✓ | Renames the DB table from `sfm_financialyear` to `ibms_financialyear` |

### Dependency graph

```
ibms/0026    sfm/0009
    │            │
    └────┬───────┘
         ▼
   ibms/0027  (CreateModel — state only)
         │
         ▼
   sfm/0010   (DeleteModel — state only)
         │
         ▼
   ibms/0028  (AlterField ×12 — state only)
         │
         ▼
   sfm/0011   (AlterField ×2 — state only)
         │
         ▼
   ibms/0029  (AlterModelTable — renames DB table)
```

---

## Source code changes

### `ibms/models.py`
- Added `FinancialYear` class definition (moved from `sfm/models.py`).
- Removed `from sfm.models import FinancialYear` import.

### `sfm/models.py`
- Removed `FinancialYear` class definition.
- Added `from ibms.models import FinancialYear` import (used by `SFMMetric.fy` and `Quarter.fy`).

### `ibms/admin.py`
- Added `FinancialYearAdmin` (moved from `sfm/admin.py`).
- Added `FinancialYear` to the model imports.

### `sfm/admin.py`
- Removed `FinancialYearAdmin` and `FinancialYear` from imports.

### `ibms/forms.py`
- Changed `from sfm.models import FinancialYear` → `from ibms.models import FinancialYear`.

### `ibms/views.py`
- Changed `from sfm.models import FinancialYear` → `from ibms.models import FinancialYear`.

### `ibms/test_views.py`
- Removed `from sfm.models import FinancialYear`; added `FinancialYear` to the `ibms.models` import block.

### `sfm/forms.py`
- Removed `FinancialYear` from `sfm.models` import; added `from ibms.models import FinancialYear`.

### `sfm/tests.py`
- Removed `FinancialYear` from `sfm.models` import; added `from ibms.models import FinancialYear`.

---

## Models with FK references to `FinancialYear`

All of the following have a `fy` field that is a `ForeignKey` to `FinancialYear`:

**ibms app**
- `IBMData`
- `DepartmentProgram`
- `GLPivDownload`
- `CorporateStrategy`
- `NCStrategicPlan`
- `GeneralServicePriority`
- `NCServicePriority`
- `PVSServicePriority`
- `SFMServicePriority`
- `ERServicePriority`
- `Outcome`
- `ServicePriorityMapping`

**sfm app**
- `SFMMetric`
- `Quarter`

---

## Applying the migrations

```bash
source .venv/bin/activate
python manage.py migrate
```

---

## Verification

All 127 unit tests pass after these changes:

```
Ran 127 tests in 196.353s
OK
```
