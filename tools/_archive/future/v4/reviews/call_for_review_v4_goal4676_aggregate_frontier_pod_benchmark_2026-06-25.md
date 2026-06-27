# Call For Review: V4 Goal4676 Aggregate-Frontier Focused POD Benchmark

Date: 2026-06-25

Requested verdict labels:

- `accept_goal4676_pass_continue_goal4677_candidate_decision_no_release`
- `accept_with_required_amendments`
- `reject_goal4676_result_or_denominator`

## Files To Review

- `future/v4/v4_goal4676_aggregate_frontier_pod_benchmark_2026-06-25.md`
- `future/v4/evidence/v4_goal4676_aggregate_frontier_pod_benchmark_2026-06-25.json`
- `future/v4/evidence/v4_goal4676_serious_2026-06-25/summary.json`
- `future/v4/evidence/v4_goal4676_serious_2026-06-25/v2_14_serious.json`
- `future/v4/evidence/v4_goal4676_serious_2026-06-25/v3_0_2_serious.json`
- `future/v4/evidence/v4_goal4676_serious_2026-06-25/v4_current_serious.json`
- `scripts/v4_goal4676_aggregate_frontier_pod_benchmark.py`
- `src/rtdsl/v4_aggregate_frontier.py`
- `src/rtdsl/v4_goal4676_aggregate_frontier_protocol.py`
- `tests/v4_goal4676_aggregate_frontier_protocol_test.py`
- `tests/v4_goal4675_aggregate_frontier_prepared_runner_test.py`

## Review Questions

1. Does the evidence support the label
   `goal4676_pass_true_v4_aggregate_frontier_candidate`?
2. Is the V2.14 denominator still honest and serious: OptiX aggregate-frontier
   host row collection plus explicit continuation, not a toy CPU-only path?
3. Does the result correctly distinguish V4-over-V2.14 speedup from V4-over-V3.0.2
   parity?
4. Is the correctness evidence sufficient for this focused gate?
5. Does the result preserve the rule that partner migration is not counted as a
   V4 runtime speed win?
6. Is it acceptable to continue to Goal4677 candidate promotion/no-go, while
   preserving no-release authorization?
7. Are any release/public wording claims accidentally authorized by the report?

## Expected Non-Authorization

Even if accepted, this review must not authorize V4 release, public speedup
wording, whole-app high-performance wording, broad V4-over-V2/V3 claims,
RT-core speedup wording, true-zero-copy wording, Tier-3 callback/PTX support,
raw OptiX callbacks, C ABI, embedding, non-Python hosts, automatic partner
selection, or app-identity native kernels.
