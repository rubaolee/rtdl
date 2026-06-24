# Goal4431 V3.0 M34 Barnes-Hut Frontier Lowering Refresh

## Decision

M34 refreshes the Barnes-Hut aggregate-frontier native-lowering evidence under
the current V3 contract language. It does not close the full Barnes-Hut bridge
debt. It deliberately measures the existing generic
`generic_aggregate_frontier_collect_2d_v1` Embree and OptiX wrappers and records
the crucial limitation: the current wrappers return host-materialized frontier
rows, so they are not yet a clean device-resident producer for the grouped-vector
partner continuation measured in M32.

## Measured Evidence

The formal pod evidence is:

- `docs/reports/goal4431_v3_0_m34_barnes_hut_frontier_lowering_refresh_8192_2026-06-16.json`

The measured evidence case uses 8,192 deterministic weighted points, bucket
size 64, theta 0.5, one warmup, and three timed repeats on the RTX 4000 Ada
pod. The generated bucketized tree has 341 nodes and the same-contract frontier
contains 3,440,003 rows.

| Backend | Native symbol | Contract | Frontier rows | Median wrapper time | Timed samples | Notes |
|---|---|---|---:|---:|---|---|
| RTDL Embree | `rtdl_embree_collect_aggregate_frontier_2d` | `generic_aggregate_frontier_collect_2d_v1` | 3,440,003 | 7.799381 s | 8.199646, 7.799381, 7.762464 s | host-materialized frontier rows |
| RTDL OptiX | `rtdl_optix_collect_aggregate_frontier_2d` | `generic_aggregate_frontier_collect_2d_v1` | 3,440,003 | 7.759663 s | 8.132503, 7.759663, 7.742843 s | host-materialized frontier rows |

Both rows matched the CPU reference exactly. OptiX is only 1.005x faster than
Embree by median for this contract, which is effectively a tie for the question
we care about.

## Interpretation

This target is intentionally diagnostic. If OptiX and Embree are close here,
that is not evidence that RT cores cannot help Barnes-Hut. It means the measured
contract is the old host-row frontier collector, where millions of rows are
materialized before any partner-side force/vector reduction can run.

The next real Barnes-Hut optimization target is therefore not another
row-materialized timing pass. It is a device-resident aggregate-frontier column producer
that can feed a same-stream partner grouped-vector or exact-force continuation
without host row materialization.

## Boundary

M34 authorizes no public speedup wording, no RT-core speedup wording, no
whole-app Barnes-Hut wording, no true-zero-copy wording, and no RT-BarnesHut
paper-reproduction wording. Its purpose is to preserve same-contract evidence
and make the remaining bridge debt explicit.
