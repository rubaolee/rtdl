# Goal3527: v2.8 Performance Recovery And Promoted-Path Plan

Date: 2026-06-05

Status: proposal for 3-AI consensus before implementation.

## User Problem

Goal3524 produced a fair same-runner OptiX comparison between the accepted
v2.3-era evidence checkout and current v2.8 on the same RTX A5000. The result
is useful as a diagnostic, but it is not acceptable as the final v2.8
performance story:

| Row | v2.8 speedup vs v2.3 same-runner |
| --- | ---: |
| `triangle_counting` | 0.992x |
| `robot_collision` | 0.990x |
| `raydb_style` count | 0.987x |
| `contact_manifold` | 0.973x |
| `barnes_hut` node coverage | 0.401x |
| `rt_dbscan` grouped stream | 1.111x |
| `spatial_rayjoin` prepared route | 1.096x |
| `rtnn` ranked summary | 1.038x |
| `librts_spatial_index` | 1.002x |

The user is right: after many days of performance work, this cannot be treated
as the headline result. Goal3524 must be treated as a **same-runner diagnostic
table**, not the final promoted-v2.8 table.

## Goal

Before any further implementation, get 3-AI consensus on the next engineering
move:

1. keep the Goal3524 same-runner table as the fair diagnostic baseline;
2. build a separate v2.8 **promoted-path performance table** that measures the
   actual v2.8 optimized paths, not only the old Goal2626 runner contracts;
3. repair or explain every weak same-runner row, starting with the Barnes-Hut
   node-coverage regression;
4. run all resulting performance evidence on one RTX pod profile with explicit
   partner/backend/contract metadata;
5. preserve RTDL's app-agnostic engine boundary: no app-specific native-engine
   shortcuts are allowed.

## Design Rules

- Primitive-first remains the rule. A fused RTDL primitive wins over partner
  continuation when it expresses the work.
- Partners remain explicit. Current benchmark partner continuations are CuPy
  where needed; PyTorch must not silently enter the current v2.8 performance
  path.
- The app developer does not write OptiX code in v2.8. Users write Python plus
  RTDL primitives, and optionally explicit partner code such as CuPy/Numba.
- A performance win must name the exact contract, backend, partner, scale,
  metric phase, and artifact path.
- No public speedup wording, release wording, whole-app wording, broad RT-core
  wording, package-install wording, true-zero-copy wording, or paper-reproduction
  wording is authorized by this goal.
- No implementation should start until Codex, Claude, and Gemini agree this is
  the right next move or revise it into an accepted plan.

## Workstream A: Promoted-Path v2.8 Table

Create a second table that measures the real v2.8 optimized paths. This table
must sit next to, not replace, Goal3524's same-runner diagnostic table.

Required columns:

- app;
- v2.3 evidence baseline contract;
- v2.8 promoted contract;
- whether the contract is same-contract, evolved-contract, or capability-new;
- backend;
- partner, if any;
- scale;
- metric source;
- setup/warmup/query/continuation timing separation;
- correctness/oracle status;
- artifact path;
- claim boundary.

Required timing-methodology fields:

- `case_repeat` or equivalent repeat count;
- whether the reported number is single-pass, median-of-N, tail median, or
  best-of-N;
- scale selected for the row;
- a `sub_millisecond_measurement_guard` field for any primary metric below
  1 ms.

For any promoted-path row whose primary metric is below 1 ms, the artifact must
record either:

1. a larger scale that moves the measured steady-state query phase above 1 ms;
2. enough repeated steady-state timing to make launch/timer noise visible and
   bounded; or
3. an explicit classification that the row is launch-overhead dominated and
   must not be used as a positive speedup headline.

The table must not collapse evolved app contracts into fake ratios. If v2.8
split an app into count/parity, relation columns, overlay area, or continuation
rows, those rows must be reported separately.

Before the RayJoin promoted-path rows are measured, Codex must write a preflight
note listing which of these contracts are already runnable entry points and
which require new authoring:

- count/parity;
- relation columns;
- shape-pair payload;
- overlay-area continuation.

If any required RayJoin promoted contract is not already runnable, contract
authoring must be sequenced as implementation work before measurement. The
performance table must not pretend that a non-runnable contract has evidence.

## Workstream B: Weak Same-Runner Recovery

The weak rows from Goal3524 get a repair ladder:

| Priority | Row | Required action |
| --- | --- | --- |
| P0 | `barnes_hut_optix_node_coverage` | Diagnose the 0.401x/0.503x regression under the same contract. Identify whether the slowdown comes from codegen, launch structure, prepared-handle setup, threshold parameters, or generic bookkeeping. Target: recover to at least parity against v2.3 same-runner before any positive v2.8 performance positioning. |
| P1 | `spatial_rayjoin_optix_prepared_full_route` | Stop using the old 1.096x row as the RayJoin headline. Measure the promoted v2.8 RayJoin paths: count/parity, relation columns, shape-pair payload, and overlay-area continuation, each as its own row. |
| P1 | `rt_dbscan_optix_grouped_stream` | Measure the promoted grouped-stream path at larger scales where continuation work is not launch-overhead dominated. Keep CuPy explicit. |
| P2 | `rtnn_optix_prepared_3d_ranked_summary` | Separate uniform/clustered/shell distributions and identify whether v2.8 optimized batch/replay paths are being exercised by the comparison row. |
| P2 | `librts_optix_aabb_index` | Increase scale and phase-split setup/query to decide whether 1.002x is true parity or launch noise. |
| P2 | `triangle_counting_optix_rt_graph_2a1_partner` | Treat the same-runner 0.992x/1.025x as parity/noise unless a promoted-path row shows a real win. Confirm CuPy-only partner path and no hidden PyTorch carrier. |
| P2 | `robot_collision_optix_prepared_device_buffers` | Phase-split and increase work so the row is not dominated by small-query launch overhead. |
| P2 | `raydb_optix_partner_resident_count` | Separate count from sum. Sum is a real win; count is flat. Decide whether count is already near the primitive lower bound or needs a scale/phase repair. |
| P2 | `contact_manifold_optix_aabb_broadphase_collect_k` | Treat current numbers as parity/noise and compare against any promoted v2.8 witness-output path separately. |

Barnes-Hut quantitative close rule:

- `recovered`: v2.8 reaches at least 0.95x of the v2.3 evidence timing on the
  same-runner node-coverage contract in two fresh RTX runs;
- `improved_but_open`: v2.8 improves materially but remains below 0.95x;
- `honest_regression`: after two focused investigation goals or one root-cause
  proof, the row remains below 0.95x and must be carried as an explicit
  regression rather than blocking all other promoted-path measurement forever.

No positive v2.8 positioning may hide an `honest_regression` Barnes-Hut row.

## Workstream C: Pod Evidence Protocol

Use a single RTX pod profile per packet. The next pod packet must record:

- SSH endpoint and key used;
- GPU name, driver, CUDA, OptiX SDK path;
- exact v2.3 evidence commit and v2.8 commit;
- dirty status;
- `RTDL_OPTIX_LIBRARY`;
- command lines;
- per-row timeout and progress logging;
- compact tracked artifact plus remote raw artifact paths.

For rows below roughly one millisecond, add either larger scale or repeated
steady-state timing. Do not present launch-noise rows as strong performance
claims.

## Workstream D: Acceptance Gates

This goal is accepted only if reviewers agree to all of these gates:

1. Goal3524 remains a diagnostic same-runner table, not a final headline.
2. The final performance story requires a promoted-path v2.8 table.
3. Barnes-Hut node coverage is a real P0 regression until investigated.
4. RayJoin's 1.096x same-runner row is not the optimized-RayJoin result.
5. CuPy is the selected partner for current promoted partner rows that need
   continuation unless a row explicitly says otherwise.
6. PyTorch must not silently appear in current v2.8 performance paths.
7. All weak rows must be repaired, scaled, or honestly classified as parity.
8. No app-specific native-engine shortcuts are allowed.
9. No public/release claim is authorized by this planning goal.
10. Sub-millisecond promoted-path rows must carry scale/repeat/timing-method
    metadata and cannot be used as speedup headlines without noise control.
11. RayJoin promoted contracts must be confirmed runnable or sequenced for
    authoring before measurement starts.

## Review Questions For Claude And Gemini

1. Is this the right next engineering move after Goal3524?
2. Is the two-table strategy clear enough: same-runner diagnostic plus promoted
   v2.8 optimized paths?
3. Are the weak-row priorities correct, especially Barnes-Hut P0 and RayJoin P1?
4. Does this plan preserve the app-agnostic engine boundary?
5. Does it correctly describe partner usage: CuPy only where explicitly selected,
   no hidden PyTorch in current v2.8 performance rows?
6. What changes are required before implementation starts?

## Validation

Local validation:

```text
PYTHONPATH=src;. py -3 -m unittest tests.goal3527_v2_8_performance_recovery_plan_test
```

## Verdict Requested

Do not implement this plan until 3-AI consensus exists.

Requested external verdict values:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`
