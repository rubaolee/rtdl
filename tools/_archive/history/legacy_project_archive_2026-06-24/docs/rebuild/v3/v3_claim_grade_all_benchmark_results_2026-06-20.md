# V3 Claim-Grade All-Benchmark Results

Status: serious V3 evidence candidate, 2026-06-20.

This is the first V3 rebuild run that covers every promoted benchmark app with
non-toy OptiX-vs-Embree evidence in one artifact.

It is strong evidence. It is still not release authorization.

## Artifact

```text
remote: /root/rtdl_v3_rebuild_20260620/artifacts/v3_claim_grade_all_benchmarks_calibrated_20260620
local:  docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620
```

Hardware:

```text
NVIDIA RTX 4000 Ada Generation, driver 550.127.05, 20475 MiB
```

Runner:

```bash
PYTHONPATH=src:. python3 scripts/v3_claim_grade_all_benchmarks.py \
  --artifact-dir /root/rtdl_v3_rebuild_20260620/artifacts/v3_claim_grade_all_benchmarks_calibrated_20260620 \
  --timeout-sec 1800
```

Result:

```text
40 rows / 40 ok / 0 failed
10 benchmark apps covered
19 comparable Embree-vs-OptiX ratios
release_authorized: false
public_speedup_claim_authorized: false
```

Second-machine confirmation:

```text
local: docs/rebuild/v3/evidence/v3_all_benchmark_lx1_confirmation_20260620
host:  lx1, NVIDIA GeForce GTX 1070, driver 580.126.09, 8192 MiB
```

The second machine passed the V3 rebuild test matrix, release wording gate, and
source-tree doctor from a clean mirror. It did not rerun the full all-app
performance suite; performance evidence in this report comes from the RTX 4000
Ada pod artifact above.

## Why This Run Exists

Earlier broad evidence tables mixed useful route-health rows with rows that were
too small or too easy to misunderstand. In particular:

- `spatial_rayjoin/rayjoin_all_backend_query_summary` used tiny fixture results
  such as `row_count=1`, `row_count=0`, and `row_count=6`;
- `librts_spatial_index/aabb_index_all_count_only` used a small 1024/512
  synthetic fixture.

Those rows remain useful boundary evidence, but they are not the all-app
performance story.

This run replaces that with calibrated serious rows:

- all ten promoted benchmark apps are included;
- RayJoin uses derived x2048 tiled workloads, not the tiny subset fixture;
- LibRTS-style AABB index uses 32768 boxes and 32768 queries;
- RTNN uses 65536-point uniform/shell/clustered distributions;
- triangle counting uses 20000 and 80000 K4 clique ladders;
- Hausdorff includes 262144-copy threshold rows;
- robot collision uses 8192 poses and 1024 obstacles, calibrated to avoid a
  single CPU baseline blocking the whole suite;
- every row keeps raw JSON, command, metric source, and boundary wording.

## App Coverage

| App | Rows | Contract | Boundary |
| --- | ---: | --- | --- |
| `hausdorff_xhd` | 8 | Prepared fixed-radius threshold decision | Not full exact Hausdorff witness materialization. |
| `spatial_rayjoin` | 6 | Authored x2048 tiled PIP/LSI/overlay scalar-count routes | Not full RayJoin paper reproduction or polygon overlay materialization. |
| `rt_dbscan` | 2 | Cluster signature on clustered 3-D fixed-radius workload | Partner-gated route; not a full paper reproduction claim. |
| `robot_collision` | 2 | Prepared collision flags | Not a full robot-planning benchmark. |
| `raydb_style` | 4 | Grouped count and sum | Torch CUDA partner gate required. |
| `barnes_hut` | 4 | Node-coverage threshold decision | Not full force aggregation. |
| `librts_spatial_index` | 2 | Generic prepared AABB index count-only route | Not LibRTS authors-code or paper-equivalent dataset timing. |
| `rtnn` | 6 | 3-D ranked nearest-neighbor summary | Distribution-specific; do not claim universal RTNN acceleration. |
| `triangle_counting` | 4 | RT-Graph 2A1 triangle-summary backend-query subpath | Synthetic K4/clique ladder, not graph database or paper-dataset reproduction. |
| `contact_manifold` | 2 | Generic 2-D AABB broadphase collect-k | Not a full physics/contact solver. |

## Ratios

Values above 1.0 mean OptiX was faster than Embree for the measured row.

| App | Row group | OptiX speedup vs Embree | Boundary |
| --- | --- | ---: | --- |
| `spatial_rayjoin` | `rayjoin_overlay_seed_authored_tiled_x2048` | 30489.613x | Hot prepared route, not whole-app or paper claim. |
| `rt_dbscan` | `dbscan_cluster_signature` | 1483.603x | Superseded by same-contract rerun; do not use as public RTDBSCAN speedup. |
| `librts_spatial_index` | `aabb_index_all_count_only_large_32768` | 814.339x | Generic AABB route, not LibRTS authors-code timing. |
| `spatial_rayjoin` | `rayjoin_lsi_authored_tiled_x2048` | 516.792x | Hot prepared route, not whole-app or paper claim. |
| `raydb_style` | `raydb_grouped_count` | 383.321x | Torch CUDA partner-gated route. |
| `raydb_style` | `raydb_grouped_sum` | 367.516x | Torch CUDA partner-gated route. |
| `triangle_counting` | `triangle_count_rt_graph_2a1_cliques_80000` | 347.232x | Synthetic RT-Graph 2A1 row. |
| `triangle_counting` | `triangle_count_rt_graph_2a1_cliques_20000` | 116.060x | Synthetic RT-Graph 2A1 row. |
| `spatial_rayjoin` | `rayjoin_pip_authored_tiled_x2048` | 10.703x | Hot prepared route, not whole-app or paper claim. |
| `robot_collision` | `prepared_collision_flags` | 5.166x | Collision-flag row only. |
| `rtnn` | `rtnn_clustered_65536_ranked_summary` | 3.333x | Distribution-specific. |
| `hausdorff_xhd` | `hausdorff_threshold_copies_16384` | 2.000x | Threshold decision row. |
| `barnes_hut` | `barnes_hut_node_coverage_bodies_32768` | 1.898x | Node-coverage row. |
| `barnes_hut` | `barnes_hut_node_coverage_bodies_131072` | 1.870x | Node-coverage row. |
| `hausdorff_xhd` | `hausdorff_threshold_copies_262144` | 1.864x | Threshold decision row. |
| `hausdorff_xhd` | `hausdorff_threshold_copies_65536` | 1.595x | Threshold decision row. |
| `contact_manifold` | `generic_aabb_broadphase_collect_k` | 1.235x | Broadphase collect-k row. |
| `rtnn` | `rtnn_shell_65536_ranked_summary` | 1.182x | Distribution-specific. |
| `rtnn` | `rtnn_uniform_65536_ranked_summary` | 1.084x | Distribution-specific and small margin. |

## What Changed Versus The Bad-Looking Rows

The earlier slow RayJoin and LibRTS-style rows were real, but they answered the
wrong user-facing performance question.

For RayJoin:

- old tiny all-workload row: subset fixture with result sizes 1, 0, and 6;
- new serious row: x2048 authored tiled workloads;
- result: OptiX candidate rows are strong, but remain hot-route and
  contract-scoped, not whole-app/paper claims.

For LibRTS-style AABB indexing:

- old tiny row: 1024 boxes, 512 point queries, 512 box queries;
- new serious row: 32768 boxes and 32768 queries;
- result: OptiX is much faster on the large same-contract generic AABB route;
- boundary: this is still not LibRTS authors-code timing or paper-equivalent
  dataset timing.

For RTDBSCAN:

- old all-app row: optimized OptiX compact-signature route compared against an
  Embree route that materializes neighbor rows and has `matches_reference:
  null`;
- fresh same-contract row: compact threshold plus the same Numba
  component-signature continuation on both backends;
- result: serious same-contract speedups are only 1.150x, 1.079x, and 1.071x;
- boundary: RTDBSCAN remains internal and not M7-qualified.

## Current User-Facing Meaning

This run is strong enough to rebuild V3 docs around row-scoped performance
evidence.

Allowed after review:

- "V3 has serious OptiX-vs-Embree candidate evidence across all ten promoted
  benchmark apps."
- "The strongest rows are route-scoped and app-specific, not a universal
  speedup claim."
- "RayDB requires partner gates; RTDBSCAN remains internal after same-contract
  rerun; RayJoin and LibRTS-style rows
  have important paper-reproduction boundaries."

Still not allowed:

- Do not claim "V3 is released."
- Do not claim "V3 broadly beats V2.x" as an unqualified claim.
- "RTDL automatically picks the fastest backend."
- "These rows reproduce RayJoin, LibRTS, RT-Graph, or other paper results."
- "Every app is fully solved end to end."

## Goal-Level Decision Audit

Decision: accept this as serious all-app V3 candidate evidence, but keep release
authorization false.

1. Did I make a foolish decision?

   The corrected decision is not foolish. The earlier over-large robot row was
   foolish because it blocked the suite without improving user evidence.

2. What actions made the earlier decision foolish?

   I mechanically used the largest existing scale for a CPU-heavy baseline
   instead of applying a per-app non-toy scale policy.

3. Was there another path?

   Yes. Calibrate scale per app, require all apps to run, and keep exact command
   and metric boundaries.

4. Can I now try a different path that truly solves the problem?

   Yes. This artifact is that path: all apps, non-toy rows, no hidden failures,
   and no release overclaim.
