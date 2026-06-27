# Call For Review: V4 Goal4628 Second Tier-2 Same-Contract Gate

Date: 2026-06-24

Requested verdict labels:

- `accept_goal4628_second_gate_existing_pod_evidence`
- `accept_with_required_amendments`
- `reject_goal4628_requires_fresh_pod_or_retarget`

## Review Request

Please critically review:

- `future/v4/v4_goal4628_second_tier2_same_contract_gate_2026-06-24.md`
- `src/rtdsl/v4_second_gate_scorecard.py`
- `tests/v4_goal4628_second_gate_scorecard_test.py`

Focused tests:

```bash
py -m unittest tests.v4_fixed_radius_device_array_api_test tests.v4_fixed_radius_docs_and_example_test tests.v4_goal4626_section8_scorecard_protocol_test tests.v4_goal4627_coverage_audit_test tests.v4_goal4628_second_gate_scorecard_test
```

Result:

- `OK`
- 22 tests

## Claim Under Review

Goal4628 accepts grouped-i64 as the second non-fixed-radius Tier-2 gate using
existing serious RTX A5000 POD evidence, without a fresh rerun unless review
finds a same-contract, product-boundary, or stale-build gap.

Target:

- app anchor: `raydb_style`
- V4 operator:
  `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
- generic primitive:
  `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D`
- continuation class:
  `grouped_i64_reduction`

POD evidence:

| Group width | Rays | Ratio |
| ---: | ---: | ---: |
| 1 | 32,768 | 166.546x |
| 1 | 131,072 | 411.867x |
| 16 | 32,768 | 11.271x |
| 16 | 131,072 | 21.369x |
| 256 | 32,768 | 1.641x |
| 256 | 131,072 | 2.978x |

All rows passed parity.

## Questions

1. Is the fixed-radius wrapper productization prerequisite sufficiently checked
   for Goal4628 review?
2. Is grouped-i64 a valid second non-fixed-radius Tier-2 gate under Goal4627?
3. Is existing POD evidence sufficient, or must Goal4628 run a fresh POD rerun?
4. Are the same-contract ratios and win source interpreted honestly?
5. Does width 256's modest 1.641x minimum require narrowing the claim, rerun, or
   rejection?
6. Does the packet preserve release, broad speedup, whole-app, true-zero-copy,
   Tier-3, CuPy, C ABI, and app-specific-kernel boundaries?
7. What amendments are required before Goal4628 can be marked complete?

## Non-Authorization

This review request does not authorize:

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
