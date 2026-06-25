# V4 Goal4628 Completion Consensus

Date: 2026-06-24

Goal: `goal4628`

Status: `complete`

Verdict: `accept_goal4628_second_gate_existing_pod_evidence`

## Objective

Accept or reject a second non-fixed-radius Tier-2 same-contract gate after the
fixed-radius anchor.

## Files Produced

- Gate packet:
  `future/v4/v4_goal4628_second_tier2_same_contract_gate_2026-06-24.md`
- Machine-checkable scorecard:
  `src/rtdsl/v4_second_gate_scorecard.py`
- Regression test:
  `tests/v4_goal4628_second_gate_scorecard_test.py`
- Call for review:
  `future/v4/reviews/call_for_review_v4_goal4628_second_tier2_same_contract_gate_2026-06-24.md`

## Verification

Command:

```bash
py -m unittest tests.v4_fixed_radius_device_array_api_test tests.v4_fixed_radius_docs_and_example_test tests.v4_goal4626_section8_scorecard_protocol_test tests.v4_goal4627_coverage_audit_test tests.v4_goal4628_second_gate_scorecard_test
```

Result:

- `OK`
- 22 tests

## Accepted Gate

- app anchor: `raydb_style`
- V4 operator: `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
- generic primitive: `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D`
- continuation class: `grouped_i64_reduction`

This gate uses existing RTX A5000 POD evidence. A fresh POD rerun is not
required before Goal4628 completion.

## Evidence Summary

| Group width | Rays/triangles | Groups | Parity | Same-contract ratio |
| ---: | ---: | ---: | :---: | ---: |
| 1 | 32,768 | 32,768 | pass | 166.546x |
| 1 | 131,072 | 131,072 | pass | 411.867x |
| 16 | 32,768 | 2,048 | pass | 11.271x |
| 16 | 131,072 | 8,192 | pass | 21.369x |
| 256 | 32,768 | 128 | pass | 1.641x |
| 256 | 131,072 | 512 | pass | 2.978x |

The minimum 1.641x row remains part of the accepted evidence. It shows that the
benefit narrows when group-row output is small; it does not invalidate the gate.

Win source:

`direct_device_output_columns_remove_legacy_group_row_host_materialization`

## Review Seats

### Claude

Verdict:

`accept_goal4628_second_gate_existing_pod_evidence`

Claude found no same-contract, stale-build, or product-boundary gap and stated
that fresh POD rerun is not required.

### Antigravity

Verdict:

`accept_goal4628_second_gate_existing_pod_evidence`

Antigravity accepted the existing RTX A5000 POD evidence and found no need for a
fresh rerun.

### Internal Reviewer: Hubble

Verdict:

`accept_goal4628_second_gate_existing_pod_evidence`

Hubble confirmed fixed-radius prerequisite, grouped-i64 validity, POD evidence
sufficiency, width-256 interpretation, and non-authorization boundaries.

## Goal-Level Decision Audit

1. Am I being foolish?

No. The decision does not rerun serious POD evidence unnecessarily, and it does
not overclaim the grouped-i64 result.

2. What actions would make this foolish?

Treating the large ratios as broad V4 speedup wording, hiding the 1.641x width
256 row, or using grouped-i64 to bypass the weighted-sum candidate decision.

3. Was there another path that avoided that failure?

Yes. Keep the scorecard same-contract, preserve every ratio, state the win
source, and send the packet for review.

4. Can the project now try a different path that solves the problem?

Yes. Goal4629 can now decide the weighted-sum candidate explicitly without
using it as the second gate.

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
