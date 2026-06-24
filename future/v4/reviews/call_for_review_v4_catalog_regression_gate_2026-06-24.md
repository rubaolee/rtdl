# Call For Review: V4 Catalog Regression Gate

Date: 2026-06-24
Requested verdict labels:

- `accept_continue_v4_engineering`
- `accept_with_required_amendments`
- `blocked_requires_rework`
- `reject_stop_this_path`

## Scope To Review

This review covers the V4 catalog regression gate:

- `scripts/v4_catalog_regression_gate.py`
- `tests/v4_catalog_regression_gate_test.py`
- `future/v4/evidence/v4_catalog_regression_gate_dry_run_2026-06-24.json`
- `future/v4/evidence/v4_catalog_regression_gate_dry_run_2026-06-24.md`
- `future/v4/evidence/v4_catalog_regression_gate_gpu_2026-06-24.json`
- `future/v4/evidence/v4_catalog_regression_gate_gpu_2026-06-24.md`
- updates to `future/v4/README.md`
- updates to `future/v4/tier2_operator_catalog.md`

It does not request V4 release authorization.

## What Was Implemented

Added one gate that runs the V4 user-facing catalog examples:

- fixed-radius count-threshold example
- closest-hit grouped-argmin example
- ray/triangle any-hit flags example
- unified V4 front-door quickstart
- Tier-2 planner example
- scalar callback Tier-3 spike-only planner example
- complex callback rejection planner example

The gate has two modes:

- `--mode dry-run`: local no-CUDA validation
- `--mode gpu`: CUDA/OptiX validation on the evidence POD

## Evidence

Local validation:

`python -m unittest tests.v4_catalog_regression_gate_test tests.v4_scope_gate_test tests.v4_frontdoor_test tests.v4_fixed_radius_docs_and_example_test`

Result: 18 tests passed.

Compile validation:

`python -m py_compile scripts/v4_catalog_regression_gate.py`

Result: passed.

Dry-run evidence:

- `future/v4/evidence/v4_catalog_regression_gate_dry_run_2026-06-24.json`
- `future/v4/evidence/v4_catalog_regression_gate_dry_run_2026-06-24.md`
- status: `passed`

POD GPU evidence:

- `future/v4/evidence/v4_catalog_regression_gate_gpu_2026-06-24.json`
- `future/v4/evidence/v4_catalog_regression_gate_gpu_2026-06-24.md`
- status: `passed`
- three GPU examples returned `status: measured`
- three GPU examples returned `correctness_passed: true`

## Questions

1. Is this an adequate regression gate for the current V4 catalog examples?
2. Does the GPU evidence prove the examples run correctly without overstating performance?
3. Are the non-authorization flags strict enough?
4. Is it acceptable that this gate validates examples, not a broad all-app benchmark?
5. What amendments are required before continuing V4 engineering?

## Non-Authorization

This review must not authorize:

- V4 release
- broad V4 speedup wording
- whole-application speedup wording
- Tier-3 callback/PTX support claims
- raw OptiX callback support
- app-specific native engine kernels
- embedding/C-ABI work

