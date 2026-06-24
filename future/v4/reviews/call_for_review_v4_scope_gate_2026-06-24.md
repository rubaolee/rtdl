# Call For Review: V4.0 Scope Gate

Date: 2026-06-24
Requested verdict labels:

- `accept_continue_v4_engineering`
- `accept_with_required_amendments`
- `blocked_requires_rework`
- `reject_stop_this_path`

## Scope To Review

This review covers the V4.0 scope gate:

- `src/rtdsl/v4_scope.py`
- `scripts/v4_scope_gate.py`
- `future/v4/v4_0_scope_gate.md`
- `future/v4/evidence/v4_scope_gate_2026-06-24.json`
- `future/v4/evidence/v4_scope_gate_2026-06-24.md`
- `tests/v4_scope_gate_test.py`
- updates to `src/rtdsl/v4.py`
- updates to `future/v4/README.md`
- updates to `future/v4/tier2_operator_catalog.md`

It does not request V4 release authorization.

## What Was Implemented

Added a machine-readable V4.0 versus V4.x boundary.

V4.0 development scope includes:

- unified Python front door
- Torch CUDA device-array input/output
- three measured Tier-2 fused generic RT operator surfaces
- conservative operator/callback planner

Deferred to V4.x:

- Tier-3 Numba/PTX/OptiX callback support
- raw OptiX callback public API
- CuPy measured performance claims
- embedding/C-ABI
- non-Python host bindings
- app-specific native engine kernels

The gate keeps release authorization false until external release review and a
release decision record exist.

## Evidence

Local validation:

`python -m unittest tests.v4_scope_gate_test tests.v4_frontdoor_test tests.v4_operator_catalog_test tests.v4_fixed_radius_docs_and_example_test`

Result: 23 tests passed.

Compile validation:

`python -m py_compile src/rtdsl/v4.py src/rtdsl/v4_scope.py scripts/v4_scope_gate.py`

Result: passed.

Generated evidence:

- `future/v4/evidence/v4_scope_gate_2026-06-24.json`
- `future/v4/evidence/v4_scope_gate_2026-06-24.md`

## Questions

1. Does this correctly define V4.0 scope without smuggling V4.x work into V4.0?
2. Is it correct to keep Tier-3 callback support deferred while keeping the planner in V4.0?
3. Are the release-blocking reasons clear and strict enough?
4. Does the gate avoid over-authorizing broad speedup, callback, embedding, or app-specific kernel claims?
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

