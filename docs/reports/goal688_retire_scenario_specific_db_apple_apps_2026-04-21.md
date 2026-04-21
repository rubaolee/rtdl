# Goal688 Retire Scenario-Specific DB And Apple Public Apps

Date: 2026-04-21

## Goal

Retire the older scenario-specific DB app entries and Apple RT app entries from
the public app surface. Keep the unified apps as the user-facing entry points:

- `examples/rtdl_database_analytics_app.py`
- `examples/rtdl_apple_rt_demo_app.py`

The retired files are not deleted because the unified apps and historical tests
still use them as compatibility helpers:

- `examples/rtdl_sales_risk_screening.py`
- `examples/rtdl_v0_7_db_app_demo.py`
- `examples/rtdl_v0_7_db_kernel_app_demo.py`
- `examples/rtdl_apple_rt_closest_hit.py`
- `examples/rtdl_apple_rt_visibility_count.py`

## Changes

- Removed the retired scenario-specific DB and Apple rows from the
  machine-readable app support matrix.
- Updated `docs/app_engine_support_matrix.md` so the only public DB app row is
  the unified DB app and the only public Apple app row is the unified Apple RT
  demo app.
- Updated `README.md`, `docs/release_facing_examples.md`,
  `docs/quick_tutorial.md`, `docs/tutorials/db_workloads.md`,
  `docs/tutorials/README.md`, `docs/README.md`, `docs/rtdl_feature_guide.md`,
  `docs/application_catalog.md`, and `examples/README.md` to point users to
  the unified apps.
- Updated the public command truth audit and tutorial/example harness so public
  commands no longer advertise the retired app scripts.
- Added `tests/goal688_retired_app_surface_test.py` to guard this policy.

## Boundaries

- This is a public-surface cleanup, not a backend semantics change.
- The retired scenario-specific files remain runnable compatibility helpers.
- Public app-level support is intentionally separate from lower-level feature
  support. Removing a row from the app matrix does not remove the underlying
  RTDL feature.

## Verification

Focused public-surface tests:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal688_retired_app_surface_test \
  tests.goal687_app_engine_support_matrix_test \
  tests.goal686_app_catalog_cleanup_test \
  tests.goal513_public_example_smoke_test

Ran 16 tests in 3.690s
OK
```

Command truth audit:

```text
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py

valid: true
public_doc_count: 14
command_count: 242
```

Additional focused guards:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal515_public_command_truth_audit_test \
  tests.goal514_tutorial_example_harness_refresh_test \
  tests.goal411_public_surface_ci_automation_test \
  tests.goal688_retired_app_surface_test

Ran 9 tests
OK
```

Static checks:

```text
PYTHONPATH=src:. python3 -m py_compile \
  src/rtdsl/app_support_matrix.py \
  examples/rtdl_database_analytics_app.py \
  examples/rtdl_apple_rt_demo_app.py \
  tests/goal688_retired_app_surface_test.py \
  scripts/goal410_tutorial_example_check.py \
  scripts/goal515_public_command_truth_audit.py

git diff --check
```

Both passed.

## Verdict

ACCEPT. The public app surface now keeps only the unified DB app and unified
Apple RT demo app while preserving retired scenario-specific scripts as
compatibility helpers.
