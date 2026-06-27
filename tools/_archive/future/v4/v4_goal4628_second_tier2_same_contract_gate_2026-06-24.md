# V4 Goal4628 Second Tier-2 Same-Contract Gate

Date: 2026-06-24

Status: `goal4628_second_tier2_gate_scorecard_not_release`

## Purpose

Goal4628 decides whether V4 has a second non-fixed-radius Tier-2 operator gate
after the fixed-radius anchor from Goal4626.

The selected gate is:

- app anchor: `raydb_style`
- V4 operator:
  `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
- generic primitive:
  `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D`
- continuation class:
  `grouped_i64_reduction`

This is an acceptance scorecard over existing serious RTX A5000 POD evidence.
It does not authorize V4 release or broad speedup wording.

## Fixed-Radius Prerequisite Check

Goal4626 carried this prerequisite:

`external_review_then_productize_fixed_radius_api_wrapper_before_second_primitive`

The prerequisite is considered satisfied for the purpose of reviewing Goal4628
because the repo contains:

- fixed-radius public V4 wrapper:
  `src/rtdsl/v4_fixed_radius.py`
- fixed-radius user documentation:
  `future/v4/fixed_radius_device_array_frontdoor.md`
- fixed-radius runnable example:
  `future/v4/examples/fixed_radius_torch_device_arrays.py`
- fixed-radius API/docs/example tests:
  `tests/v4_fixed_radius_device_array_api_test.py`
  `tests/v4_fixed_radius_docs_and_example_test.py`
- amendment closure:
  `future/v4/reviews/claude_v4_section8_device_array_frontdoor_amendment_closure_2026-06-24.md`

Focused prerequisite tests were run with Goal4628 checks:

```bash
py -m unittest tests.v4_fixed_radius_device_array_api_test tests.v4_fixed_radius_docs_and_example_test tests.v4_goal4626_section8_scorecard_protocol_test tests.v4_goal4627_coverage_audit_test
```

Result:

- `OK`
- 18 tests

## Evidence

Machine-checkable scorecard:

- `src/rtdsl/v4_second_gate_scorecard.py`

Regression test:

- `tests/v4_goal4628_second_gate_scorecard_test.py`

Primary grouped-i64 evidence:

- `future/v4/evidence/v4_goal4617_grouped_i64_width1_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_goal4617_grouped_i64_width16_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_goal4617_grouped_i64_width256_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/reviews/claude_v4_goal4617_grouped_i64_promotion_decision_review_2026-06-24.raw.md`
- `future/v4/reviews/goal4627_completion_consensus_and_review_debt_2026-06-24.md`

## POD Results

All measured rows are same-contract comparisons:

- numerator: legacy host-output grouped-i64 primitive
- denominator: V4 direct device-output grouped-i64 route
- win source: direct device output columns remove legacy grouped-row host
  materialization

| Group width | Rays/triangles | Groups | Parity | Same-contract ratio |
| ---: | ---: | ---: | :---: | ---: |
| 1 | 32,768 | 32,768 | pass | 166.546x |
| 1 | 131,072 | 131,072 | pass | 411.867x |
| 16 | 32,768 | 2,048 | pass | 11.271x |
| 16 | 131,072 | 8,192 | pass | 21.369x |
| 256 | 32,768 | 128 | pass | 1.641x |
| 256 | 131,072 | 512 | pass | 2.978x |

The smallest ratio is intentionally retained in the scorecard. Width 256 has
few output groups, so legacy host materialization is less expensive and the
ratio narrows. It still remains above parity at both serious sizes.

## Gate Decision

Goal4628 gate result:

`pass_existing_pod_evidence_accepted_pending_review`

Reason:

1. The selected operator is generic and non-fixed-radius.
2. It has serious POD evidence at two ray counts and three group widths.
3. Correctness parity passed for all tested reductions.
4. All tested ratios are above parity.
5. The win source is product-boundary removal for grouped output columns, not an
   app-specific kernel.
6. Goal4627 selected this operator as the second gate.

Fresh POD rerun status:

`not_required_before_goal4628_completion`

Reason:

The existing evidence already contains serious RTX A5000 POD runs. A fresh rerun
should be required only if external review finds a same-contract,
product-boundary, or stale-build gap in the evidence.

## What This Proves

- V4 has a second non-fixed-radius generic Tier-2 operator with serious
  same-contract POD evidence.
- Direct device output can materially reduce the legacy host-output boundary for
  grouped-i64 reductions.
- The V4 operator catalog is broader than fixed-radius alone.

## What This Does Not Prove

- It does not authorize V4 release.
- It does not authorize broad V4 speedup wording.
- It does not authorize whole-application speedup wording.
- It does not prove every grouped workload will see large speedups; width 256
  shows the benefit narrows when group-row output is small.
- It does not authorize CuPy performance claims.
- It does not authorize true-zero-copy public wording.
- It does not authorize Tier-3 callback support.
- It does not authorize app-specific native kernels.

## Non-Authorization

Goal4628 does not authorize:

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
