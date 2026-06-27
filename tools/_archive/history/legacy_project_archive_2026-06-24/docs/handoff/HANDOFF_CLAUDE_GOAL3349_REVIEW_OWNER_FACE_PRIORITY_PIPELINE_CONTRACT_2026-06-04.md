# Handoff: Claude Review Goal3349 Owner-Face Priority Pipeline Contract

Please review the v2.8 RayJoin owner-face line through Goal3349, with emphasis on the new explicit-priority pipeline contract added after Goal3348.

Expected review output:

- `docs/reviews/goal3350_claude_review_goal3349_owner_face_priority_pipeline_contract_2026-06-04.md`

## Current Commit

- `b2460bee` (`Goal3349 formalize owner-face priority pipeline contract`)

## Scope

Read at minimum:

- `src/rtdsl/closed_shape_topology.py`
- `src/rtdsl/__init__.py`
- `tests/goal3349_owner_face_priority_pipeline_contract_test.py`
- `docs/reports/goal3349_owner_face_priority_pipeline_contract_2026-06-04.md`
- `docs/reports/goal3348_rayjoin_owner_face_pipeline_status_2026-06-04.md`
- `docs/reports/goal3345_priority_owner_face_membership_pipeline_reference_2026-06-04.md`
- `docs/reports/goal3342_priority_owner_face_selector_reference_2026-06-04.md`

Optional background:

- `docs/reports/goal3327_rayjoin_pip_extra_shape_id_diagnosis_2026-06-04.md`
- `docs/reports/goal3328_rayjoin_cdb_topology_shape_id_probe_2026-06-04.md`
- `docs/reports/goal3333_rayjoin_probe_point_owner_face_availability_2026-06-04.md`
- `docs/reports/goal3335_rayjoin_incident_face_owner_probe_2026-06-04.md`

## What Changed In Goal3349

- Added `OWNER_FACE_PRIORITY_PIPELINE_CONTRACT`.
- Added `owner_face_priority_pipeline_contract()`.
- Added `validate_owner_face_priority_pipeline_contract()`.
- Exported the contract through `rtdsl`.
- Added a report and focused tests.

The contract formalizes the explicit-column pipeline:

1. `incident_face_candidate_rows(point_id,face_id,incident_face_count)`
2. `priority_rows(point_id,face_id,priority)`
3. `candidate_rows(point_id,shape_id)`
4. `topology_rows(shape_id|chain_id,left_face_id,right_face_id)`

Selection rule:

- higher incident count wins,
- lower caller-supplied priority breaks ties,
- missing/tied priority fails closed,
- the native engine must not invent priority or infer app ownership.

## Validation Already Run

Focused:

```text
Ran 19 tests in 0.026s
OK
```

Full recent owner-face chain:

```text
Ran 50 tests in 0.026s
OK
```

`py_compile` passed for:

- `src/rtdsl/closed_shape_topology.py`
- `src/rtdsl/__init__.py`

## Review Questions

1. Does Goal3349 correctly formalize the explicit-priority owner-face pipeline without turning it into app-specific engine logic?
2. Are the contract fields strict enough for future native/device lowering?
3. Are `caller_policy_required`, `native_engine_may_infer_app_ownership=false`, and `native_engine_may_invent_priority=false` sufficient redlines?
4. Does the test coverage catch the important failure modes before any lowering?
5. What should be fixed before the next v2.8 engineering target?

## Required Boundaries

- Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
- No release, public speedup, broad RT-core speedup, true zero-copy, RTDL-beats-RayJoin, or RayJoin paper reproduction claims.
- Native engine must not infer CDB/RayJoin ownership semantics.
- If accepting, state exactly what remains blocked before promotion from Python reference contract to device/native implementation.
