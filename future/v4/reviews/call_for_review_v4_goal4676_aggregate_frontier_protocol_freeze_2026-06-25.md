# Call For Review: V4 Goal4676 Aggregate-Frontier Protocol Freeze

Date: 2026-06-25

Requested verdict labels:

- `accept_goal4676_protocol_run_smoke_then_serious_if_smoke_passes`
- `accept_with_required_amendments`
- `reject_goal4676_protocol_or_denominator`

## Files To Review

- `future/v4/v4_goal4676_aggregate_frontier_protocol_freeze_2026-06-25.md`
- `future/v4/evidence/v4_goal4676_aggregate_frontier_protocol_freeze_2026-06-25.json`
- `src/rtdsl/v4_goal4676_aggregate_frontier_protocol.py`
- `scripts/v4_goal4676_aggregate_frontier_pod_benchmark.py`
- `tests/v4_goal4676_aggregate_frontier_protocol_test.py`
- `future/v4/v4_goal4675_aggregate_frontier_prepared_runner_2026-06-25.md`

## Review Questions

1. Does the protocol use a serious V2.14 denominator rather than a weak CPU-only
   or toy denominator?
2. Is the V2.14 denominator stated honestly, including the requirement that
   `collect_aggregate_frontier_2d_optix` must execute or the run is
   inconclusive/reclassified?
3. Do the frozen bars prevent partner migration from being counted as a V4
   runtime speed win?
4. Is the V4 runner route tested as the Goal4675 productized front door rather
   than an app-mode bypass?
5. Are the smoke-before-serious conditions strong enough to avoid wasting POD
   time on a broken denominator?
6. Does this protocol preserve all non-authorization boundaries?

## Expected Non-Authorization

Even if accepted, this review must not authorize V4 release, public speedup
wording, whole-app high-performance wording, RT-core speedup wording,
true-zero-copy wording, Tier-3 callback/PTX support, raw OptiX callbacks, C ABI,
embedding, non-Python hosts, automatic partner selection, or app-identity native
kernels.
