# Call For Review: V4 Unified Python Front Door

Date: 2026-06-24
Requested verdict labels:

- `accept_continue_v4_engineering`
- `accept_with_required_amendments`
- `blocked_requires_rework`
- `reject_stop_this_path`

## Scope To Review

This review covers the unified V4 Python front door:

- `src/rtdsl/v4.py`
- `future/v4/README.md`
- `future/v4/examples/v4_frontdoor_quickstart.py`
- `tests/v4_frontdoor_test.py`

It does not request V4 release authorization.

## What Was Implemented

Added `import rtdsl.v4 as rtdl_v4` as the single development entry point for:

- measured fixed-radius count-threshold device-array surface
- measured closest-hit grouped-argmin device-array surface
- measured ray/triangle any-hit flags device-array surface
- measured Tier-2 operator catalog
- conservative operator/callback planner
- unified V4 claim boundary

The unified boundary keeps these claims false:

- release claim
- broad V4 speedup claim
- whole-application speedup claim
- Tier-3 callback/PTX support claim
- raw OptiX callback support claim
- app-specific native-kernel claim
- embedding/C-ABI claim

## Evidence

Local validation:

`python -m unittest tests.v4_frontdoor_test tests.v4_operator_catalog_test tests.v4_fixed_radius_docs_and_example_test`

Result: 18 tests passed.

Compile validation:

`python -m py_compile src/rtdsl/v4.py src/rtdsl/v4_operator_catalog.py future/v4/examples/v4_frontdoor_quickstart.py future/v4/examples/operator_callback_planning.py`

Result: passed.

Runnable local example:

`python future/v4/examples/v4_frontdoor_quickstart.py`

## Questions

1. Is `rtdsl.v4` an appropriate unified V4 development front door?
2. Does the front door preserve the development/non-release boundary?
3. Does it avoid over-authorizing Tier-3 callbacks, raw OptiX callbacks, or app-specific kernels?
4. Is the README clean enough as a V4 starting point without dragging users through historical churn?
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

