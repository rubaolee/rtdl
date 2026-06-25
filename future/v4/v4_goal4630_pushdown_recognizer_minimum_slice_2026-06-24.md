# V4 Goal4630 Push-Down Recognizer Minimum Slice

Date: 2026-06-24

Status: `goal4630_minimum_pushdown_recognizer_not_release`

Goal4630 implements the minimum declarative recognizer required by the V4 three-tier fused architecture design. It is not a full ITRE compiler. It recognizes one generic operator at a time, routes measured/candidate Tier-2 operators through the existing catalog, and fails closed for unsupported/action-shaped/app-identity requests.

## Purpose

The V4 design says users should not write raw OptiX callbacks as the public programming model. They should express a generic relation/reduction operator, and RTDL should push that operator down only when it is in the recognized operator library.

Goal4630 makes that boundary executable:

- recognized generic operator -> measured or candidate Tier-2 catalog plan;
- unmeasured partner -> fail closed;
- app-identity kernel -> fail closed;
- action-shaped callback -> fail closed;
- Tier-3 scalar callback -> spike-only, not push-down;
- unsupported custom logic -> fail closed.

## Implemented Surface

Code:

- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4.py`

New API:

- `rtdsl.v4_operator_catalog.recognize_v4_pushdown_request(...)`
- `rtdsl.v4.recognize_pushdown_request_v4(...)`

New result type:

- `V4PushdownRecognition`

The recognizer accepts a mapping such as:

```python
{
    "kind": "itre_relation_reduce",
    "relation": "fixed_radius",
    "reduction": "count_threshold",
}
```

and returns a machine-checkable recognition object with:

- `status`
- `pushdown_recognized`
- `fail_closed`
- `plan`
- claim-boundary flags

## Recognized Positive Routes

Measured Tier-2 examples:

- `fixed_radius` / `count_threshold`
- `primitive_grouped_reduction`
- existing aliases in `V4_OPERATOR_ALIASES`

Candidate Tier-2 example:

- `ray_triangle_any_hit_weighted_sum`

The candidate route is recognized, but remains non-measured:

- status: `pushdown_recognized_candidate_tier2_not_measured`
- measured-catalog claim authorized: false
- release claim authorized: false

## Fail-Closed Routes

The recognizer fails closed for:

- CuPy requests to Torch-only measured or candidate surfaces: `pushdown_fail_closed_unmeasured_partner`
- app-identity kernel names such as `barnes_hut`, `dbscan`, `rayjoin`, `triangle_counting`: `pushdown_fail_closed_app_identity_kernel`
- action-shaped callbacks: `pushdown_fail_closed_action_shape`
- scalar Numba callbacks: `pushdown_fail_closed_tier3_spike_only`
- unsupported custom logic: `pushdown_fail_closed_unsupported`

This intentionally prevents V4 from becoming a Python skin over arbitrary OptiX callbacks.

## Tests

Test file:

- `tests/v4_goal4630_pushdown_recognizer_test.py`

Regression context:

- `tests/v4_operator_catalog_test.py`
- `tests/v4_goal4629_weighted_sum_candidate_decision_test.py`

Focused test command:

```powershell
py -m unittest tests.v4_operator_catalog_test tests.v4_goal4630_pushdown_recognizer_test tests.v4_goal4629_weighted_sum_candidate_decision_test
```

Result:

- 23 tests passed.

## Goal-Level Decision Self-Audit

Decision: implement a minimal recognizer rather than a full compiler.

1. Am I being foolish?
   - No. Goal4630 requires a minimum slice that proves the programming model boundary; a full compiler would be a route-drift risk.

2. What actions would make this foolish?
   - Claiming this is a complete ITRE compiler.
   - Letting candidate or CuPy-unmeasured routes count as measured release surfaces.
   - Accepting app-identity kernels because they happen to be useful benchmarks.
   - Treating Tier-3 scalar callbacks as supported V4.0 push-down.

3. Is there another path that avoids being stuck on one idea?
   - Yes. The recognizer delegates to the existing planner/catalog, so future operators can be added without changing the boundary rules.

4. Can I start a different path that truly solves the problem?
   - Yes. Goal4631 can now settle the Tier-3 spike honestly because Goal4630 already tells users that Tier-3 is not the public push-down model.

## Non-Authorization

Goal4630 does not authorize:

- V4 release
- V4 release-candidate status
- measured-catalog promotion
- broad V4 speedup claims
- whole-application speedup claims
- true-zero-copy public wording
- Tier-3 callback support
- raw OptiX callback support
- CuPy performance claims
- C ABI / embedding / non-Python-host work
- app-specific native kernels
