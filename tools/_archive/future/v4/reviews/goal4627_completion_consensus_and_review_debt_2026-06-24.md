# V4 Goal4627 Completion Consensus And Review Debt

Date: 2026-06-24

Goal: `goal4627`

Status: `complete`

Verdict: `accept_goal4627_coverage_audit`

## Objective

Audit how the current V4 Tier-2 operator catalog maps to the promoted benchmark
apps, identify uncovered/deferred rows, and select the second Tier-2
same-contract gate for Goal4628.

## Files Produced

- Coverage audit document:
  `future/v4/v4_goal4627_tier2_operator_coverage_audit_2026-06-24.md`
- Machine-checkable audit rows:
  `src/rtdsl/v4_coverage_audit.py`
- Regression test:
  `tests/v4_goal4627_coverage_audit_test.py`
- Call for review:
  `future/v4/reviews/call_for_review_v4_goal4627_tier2_operator_coverage_audit_2026-06-24.md`
- Antigravity debt:
  `future/v4/reviews/antigravity_v4_goal4627_tier2_operator_coverage_audit_review_blocked_2026-06-24.md`

## Verification

Command:

```bash
py -m unittest tests.v4_goal4627_coverage_audit_test
```

Result:

- `OK`
- 4 tests

## Coverage Result

The audited set is the 10 promoted benchmark apps:

- `strong_measured_operator_coverage`: 1
- `partial_measured_operator_coverage`: 5
- `candidate_not_measured_release_coverage`: 1
- `deferred_or_uncovered_v4_0`: 3

This is not an 80% coverage claim and does not authorize public coverage
wording. It is an engineering audit for V4 planning.

## Goal4628 Recommendation

Recommended next gate:

- app anchor: `raydb_style`
- operator: `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
- generic primitive: `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D`
- continuation class: `grouped_i64_reduction`

Reason:

- non-fixed-radius
- generic operator, not app-identity
- serious RTX A5000 POD evidence exists
- prior external promotion review exists
- avoids using weighted-sum while it remains candidate-only

## Required Amendment Closed

Claude initially returned:

`accept_with_required_amendments`

Required amendment:

- Explain why `triangle_counting` remains candidate-bound even though its mapped
  operators include measured grouped-i64.

Closure:

- `triangle_counting.release_gap` now states that grouped-i64 covers an adjacent
  grouped-reduction dimension but not triangle counting's dominant any-hit
  weighted/count continuation path.
- The audit document mirrors that explanation.
- The regression test asserts both phrases:
  - `adjacent grouped-reduction dimension`
  - `dominant any-hit weighted/count continuation path`

Claude amendment-check verdict:

`accept_goal4627_coverage_audit`

## Review Seats

### Claude

Final verdict:

`accept_goal4627_coverage_audit`

Claude verified the amendment in code, test, and documentation.

### Internal Reviewer: Gauss

Verdict:

`accept_goal4627_coverage_audit`

Gauss confirmed:

- all 10 promoted apps are covered
- the 1/5/1/3 split is asserted in tests
- `triangle_counting` is correctly candidate-bound
- `barnes_hut`, `spatial_rayjoin`, and `librts_spatial_index` remain deferred
- `raydb_style` / grouped-i64 is a sound Goal4628 recommendation
- no release/broad-speedup/Tier3/CuPy/C ABI/app-kernel overclaiming was found

### Antigravity

Status:

`blocked_empty_stdout_review_debt`

Both Antigravity attempts returned exit code `0` with empty stdout and empty
stderr. They are recorded as debt, not substantive review seats.

## Goal-Level Decision Audit

1. Am I being foolish?

No after amendment. The audit now avoids a subtle but important shortcut: it
does not treat measured grouped-i64 as enough to promote triangle counting while
weighted-sum remains candidate-only.

2. What actions would have made this foolish?

Leaving `triangle_counting` classified as candidate without explaining why the
measured grouped-i64 operator did not upgrade it to partial measured coverage.

3. Was there another path that avoided that failure?

Yes. Make the classification reason explicit in code, docs, and test.

4. Can the project now try a different path that actually solves the problem?

Yes. Goal4628 can use `raydb_style` / grouped-i64 as the second same-contract
Tier-2 gate, subject to the fixed-radius wrapper prerequisite from Goal4626.

## Non-Authorization

Goal4627 does not authorize:

- V4 release
- V4 release-candidate status
- public broad speedup wording
- whole-application speedup wording
- public true-zero-copy wording
- Tier-3 callback support
- raw OptiX callback support
- CuPy performance claims
- C ABI / embedding / non-Python-host work
- app-specific native kernels
