# Call For Review: V4 Operator/Callback Planner Boundary

Date: 2026-06-24
Requested verdict labels:

- `accept_continue_v4_engineering`
- `accept_with_required_amendments`
- `blocked_requires_rework`
- `reject_stop_this_path`

## Scope To Review

This review covers the new V4 operator/callback planner boundary:

- `src/rtdsl/v4_operator_catalog.py`
- `future/v4/callback_and_operator_planning.md`
- `future/v4/examples/operator_callback_planning.py`
- `tests/v4_operator_catalog_test.py`
- updates to `future/v4/tier2_operator_catalog.md`
- updates to `tests/v4_fixed_radius_docs_and_example_test.py`

It does not request V4 release authorization.

## What Was Implemented

Added a conservative programmatic planner:

- recognized measured Tier-2 operators route to measured device-array surfaces
- CuPy remains declared but unmeasured
- scalar Numba device callbacks are classified as Tier-3 spike-only
- action-shaped callbacks with shared mutation, dynamic allocation, or
  variable-length output are rejected/deferred for V4.0
- raw OptiX callbacks and app-specific native kernels remain unauthorized

## Evidence

Local validation:

`python -m unittest tests.v4_operator_catalog_test tests.v4_fixed_radius_docs_and_example_test`

Result: 14 tests passed.

Compile validation:

`python -m py_compile src/rtdsl/v4_operator_catalog.py future/v4/examples/operator_callback_planning.py`

Result: passed.

Runnable local example:

```bash
python future/v4/examples/operator_callback_planning.py --case tier2
python future/v4/examples/operator_callback_planning.py --case scalar-callback
python future/v4/examples/operator_callback_planning.py --case complex-callback
```

## Questions

1. Does this planner answer the user problem of complex custom callbacks without pretending arbitrary OptiX callbacks are supported?
2. Is the Tier-2/Tier-3/deferred classification strict enough?
3. Is it acceptable that scalar Numba callbacks are only `tier3_spike_only_not_v4_0_release_surface`?
4. Does the planner accidentally over-authorize release, speedup, callback, or app-specific native-kernel claims?
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

