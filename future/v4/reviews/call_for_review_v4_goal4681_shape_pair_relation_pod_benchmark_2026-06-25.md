# Call For Review: V4 Goal4681 Shape-Pair Relation POD Benchmark

Date: 2026-06-25

Requested verdict labels:

- `accept_goal4681_no_speed_credit_do_not_promote_continue_goal4682`
- `reject_goal4681_due_to_bad_denominator_or_bad_dataset`
- `accept_with_required_amendments_before_goal4682`

## Review Target

- Report:
  `future/v4/v4_goal4681_shape_pair_relation_pod_benchmark_2026-06-25.md`
- Evidence directory:
  `future/v4/evidence/v4_goal4681_shape_pair_serious_2026-06-25/`
- Summary:
  `future/v4/evidence/v4_goal4681_shape_pair_serious_2026-06-25/summary.json`
- Code:
  `scripts/v4_goal4681_shape_pair_relation_pod_benchmark.py`
  `src/rtdsl/v4_goal4681_shape_pair_relation_result.py`
- Tests:
  `tests/v4_goal4681_shape_pair_benchmark_script_test.py`
  `tests/v4_goal4681_shape_pair_result_test.py`

## Main Finding

Goal4681 ran correctly but did not produce speed credit.

Serious 4096-shape generated focused input:

| Ratio | Value |
| --- | ---: |
| V4/V2.14 hot | 0.963x |
| V4/V2.14 wall | 0.605x |
| V4/V3.0.2 hot | 0.977x |

Correctness/count parity passed. V4 hot-path row-stream materialization was
false. Performance bars failed.

## Questions

1. Is the generated 4096-shape focused CDB input acceptable for this
   same-primitive route probe, given that it is explicitly not RayJoin paper or
   app-level evidence?
2. Is the V2.14 denominator still valid and strong enough?
3. Is the no-promotion/no-speed-credit conclusion correct?
4. Should this route remain internal/productization-only?
5. Should Goal4682 select a different target rather than continuing to tune
   shape-pair active count?

## Non-Authorization To Preserve

This review must not authorize:

- V4 release.
- public speedup wording.
- broad V4-over-V2/V3 claims.
- whole-app high-performance wording.
- measured-catalog promotion for this route.
- app-identity native kernels.
- partner migration as speed evidence.
- Tier-3 callbacks or embedding/C ABI work.
