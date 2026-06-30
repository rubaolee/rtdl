# Goal2637 All Benchmark Performance Diffs

Date: 2026-05-27

Status: internal measured performance report. This is not public speedup
wording.

## Source Artifacts

Primary all-benchmark standard matrix:

- `docs/reports/goal2634_full_standard_prepared_contact_pod/summary.md`
- `docs/reports/goal2634_full_standard_prepared_contact_pod/summary_slim.json`

Machine-readable consolidated table:

- `docs/reports/goal2637_all_benchmark_perf_diffs_2026-05-27.json`

Strengthened rows for the five previously weak apps:

- `docs/reports/goal2636_strengthened_rows_pod_fixed/summary.md`
- `docs/reports/goal2636_strengthened_rows_pod_fixed/summary.json`
- `docs/reports/goal2636_strengthened_rows_stress_pod_fixed/summary.md`
- `docs/reports/goal2636_strengthened_rows_stress_pod_fixed/summary.json`

Large generated raw inputs from the strengthened run, such as RTNN point CSVs
and triangle edge files, were not retained locally because the runner can
regenerate them deterministically. The retained summaries and per-case JSON
outputs are the evidence artifacts used here.

Supporting stress/addendum artifacts:

- `docs/reports/goal2626_benchmark_embree_optix_stress_addendum_2026-05-26.md`
- `docs/reports/goal2626_robot_collision_stress_pod_32768x512/compact_summary.json`
- `docs/reports/goal2626_contact_aabb_collect_stress_pod_65536/summary.json`
- `docs/reports/goal2628_rtnn_large_envfixed_pod/summary.json`

Primary pod environment:

| Item | Value |
| --- | --- |
| Pod | `root@203.57.40.101 -p 10165` |
| GPU | NVIDIA RTX A5000, driver 565.57.01, 24564 MiB |
| Standard matrix commit | `56e1f9b230cdef6d803191c8804f192133b4d020` |
| Strengthened runner base checkout | `/root/rtdl_goal2627/rtdl` plus synced local Goal2636 runner/report/fixture changes |
| Fixed strengthened-run environment | `source /root/rtdl_goal2627/venv/bin/activate`; `RTDL_OPTIX_PTX_COMPILER=nvcc`; `RTDL_NVCC=/usr/local/cuda-12.6/bin/nvcc`; `RTDL_OPTIX_PTX_ARCH=compute_86`; CUDA 12.6 library paths |

## Executive Result

The current measured portfolio has:

- 10 promoted benchmark apps.
- 11 standard comparison rows because RayDB has grouped-count and grouped-sum
  contracts.
- 13 additional strengthened rows for Hausdorff, Spatial RayJoin, RTNN,
  Barnes-Hut, and triangle counting.
- 16 stress rows for the same five apps.

Measured outcome:

| Matrix | Rows | OptiX wins | Min speedup | Median speedup | Geomean speedup | Max speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Goal2634 standard all-benchmark matrix | 11 | 11 | 3.29x | 29.95x | 32.25x | 280.15x |
| Goal2636 strengthened weak-row matrix | 13 | 13 | 1.81x | 23.38x | 16.90x | 170.63x |
| Goal2636 strengthened stress matrix | 16 | 16 | 1.26x | 36.36x | 21.69x | 465.45x |

The strengthened run removes the previous immediate blocker for the five weak
apps: the current measured evidence now has larger or stronger workload
coverage for Hausdorff, Spatial RayJoin, RTNN, Barnes-Hut, and triangle
counting, and the OptiX path wins every recorded strengthened ratio row.

## Standard Matrix Diffs

| App | Comparison group | Embree sec | OptiX sec | OptiX speedup | Interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| Hausdorff / X-HD-style | threshold decision | 0.102451 | 0.0311073 | 3.29x | Valid threshold-decision subpath. |
| Spatial RayJoin-style | all-backend scoped query summary | 0.0203149 | 0.000529638 | 38.36x | Valid scoped route, but superseded by stronger nonzero tiled route rows below. |
| RT-DBSCAN-style | cluster signature | 20.6102 | 1.62144 | 12.71x | Strong app-contract baseline; generic grouped-stream continuation, no DBSCAN-native ABI. |
| Robot collision | prepared collision flags | 0.00853798 | 0.00161413 | 5.29x | Strong prepared-query baseline. |
| RayDB-style grouped aggregate | grouped count | 0.222185 | 0.000793088 | 280.15x | Strong partner-resident grouped count; not an RT-core traversal claim. |
| RayDB-style grouped aggregate | grouped sum | 0.243746 | 0.000977349 | 249.40x | Strong partner-resident grouped sum; not an RT-core traversal claim. |
| Barnes-Hut / RT-BarnesHut-style | node coverage prepared threshold decision | 0.0388851 | 0.00855045 | 4.55x | Valid node-coverage contract; strengthened below. |
| LibRTS-style spatial index | AABB index all count-only | 20.7070 | 0.691477 | 29.95x | Strong count-only AABB index contract. |
| RTNN neighbor search | prepared 3-D ranked summary | 0.263800 | 0.00153247 | 172.14x | Valid ranked-summary contract; strengthened distribution ladder below. |
| Triangle counting | RT-Graph-style RT-2A1 summary | 0.0390490 | 0.000364401 | 107.16x | Valid generic RT-Graph 2A1 backend-query contract; strengthened below. |
| Bounded contact witness / contact-manifold | generic AABB broadphase + bounded collection | 0.485812 | 0.0184764 | 26.29x | Strong generic AABB row discovery plus bounded collection. |

## Strengthened Rows For Previously Weak Apps

These rows were run after fixing the pod environment to use the same nvcc/PTX
and CuPy venv policy as the earlier calibrated runs. The unfixed first attempt
is intentionally not used as performance evidence because it failed from
environment setup, not app logic.

| App | Strengthened workload | Embree sec | OptiX sec | OptiX speedup | Interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| Hausdorff / X-HD-style | threshold, 4096 copies | 0.100719 | 0.0344760 | 2.92x | OptiX wins at small/standard scale. |
| Hausdorff / X-HD-style | threshold, 16384 copies | 0.380607 | 0.181478 | 2.10x | OptiX wins at larger scale. |
| Hausdorff / X-HD-style | threshold, 65536 copies | 1.70826 | 0.946120 | 1.81x | OptiX still wins; margin narrows as scale rises. |
| Spatial RayJoin-style | PIP authored tiled x512 | 0.0233497 | 0.000315720 | 73.96x | Nonzero tiled point-in-polygon route. |
| Spatial RayJoin-style | LSI authored tiled x512 | 0.0298779 | 0.000303850 | 98.33x | Nonzero tiled line-segment-intersection route. |
| Spatial RayJoin-style | overlay-seed authored tiled x512 | 0.266497 | 0.0558806 | 4.77x | Nonzero overlay dependency route; still not full polygon overlay materialization. |
| RTNN neighbor search | uniform 65536 ranked summary | 0.258464 | 0.0106400 | 24.29x | OptiX wins under uniform distribution. |
| RTNN neighbor search | clustered 65536 ranked summary | 2.16539 | 0.0926344 | 23.38x | OptiX wins under density-risk clustered distribution. |
| RTNN neighbor search | shell 65536 ranked summary | 0.934770 | 0.00547840 | 170.63x | OptiX wins under shell distribution. |
| Barnes-Hut / RT-BarnesHut-style | node coverage, 8192 bodies | 0.0393546 | 0.00862844 | 4.56x | Same-contract node-coverage row remains positive. |
| Barnes-Hut / RT-BarnesHut-style | node coverage, 32768 bodies | 0.113009 | 0.0374079 | 3.02x | Current same-contract app-internal timing overturns the older process-wall loss. |
| Triangle counting | RT-Graph 2A1, 5000 K4 cliques | 0.0490641 | 0.000372456 | 131.73x | Generic RT-Graph backend-query row remains positive. |
| Triangle counting | RT-Graph 2A1, 20000 K4 cliques | 0.102953 | 0.000755426 | 136.28x | Current generic RT path overturns the older fallback/process-wall loss. |

Additional OptiX-only Hausdorff exact-witness rows also succeeded:

| App | OptiX-only exact row | OptiX sec | Why not ratioed |
| --- | --- | ---: | --- |
| Hausdorff / X-HD-style | exact grouped seeded/pruned witness, 8192 points | 0.991919 | No same exact-witness Embree route in the current harness. |
| Hausdorff / X-HD-style | exact grouped seeded/pruned witness, 32768 points | 1.45300 | No same exact-witness Embree route in the current harness. |

## Stress Rows For Previously Weak Apps

The stress run used the same fixed pod environment and increases workload sizes
for the same five apps.

| App | Stress workload | Embree sec | OptiX sec | OptiX speedup | Interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| Hausdorff / X-HD-style | threshold, 16384 copies | 0.369679 | 0.164627 | 2.25x | OptiX win. |
| Hausdorff / X-HD-style | threshold, 65536 copies | 1.69796 | 1.01777 | 1.67x | OptiX win; margin narrows. |
| Hausdorff / X-HD-style | threshold, 262144 copies | 7.31725 | 4.63951 | 1.58x | OptiX still wins at largest threshold scale tested. |
| Spatial RayJoin-style | PIP authored tiled x2048 | 0.0349485 | 0.000510602 | 68.45x | Nonzero tiled PIP route remains strongly positive. |
| Spatial RayJoin-style | LSI authored tiled x2048 | 0.0356758 | 0.000455981 | 78.24x | Nonzero tiled LSI route remains strongly positive. |
| Spatial RayJoin-style | overlay-seed authored tiled x2048 | 3.78287 | 0.897468 | 4.22x | Overlay-seed remains positive but is the weakest RayJoin route. |
| RTNN neighbor search | uniform 65536 ranked summary | 0.262757 | 0.00226594 | 115.96x | OptiX win. |
| RTNN neighbor search | clustered 65536 ranked summary | 2.11638 | 0.0933383 | 22.67x | OptiX win under density pressure. |
| RTNN neighbor search | shell 65536 ranked summary | 0.866792 | 0.00552687 | 156.83x | OptiX win. |
| RTNN neighbor search | uniform 262144 ranked summary | 3.15816 | 0.00990457 | 318.86x | OptiX win at larger uniform scale. |
| RTNN neighbor search | clustered 262144 ranked summary | 14.9944 | 1.37452 | 10.91x | OptiX win; clustered density is the hardest RTNN case. |
| RTNN neighbor search | shell 262144 ranked summary | 9.35380 | 0.186924 | 50.04x | OptiX win at larger shell scale. |
| Barnes-Hut / RT-BarnesHut-style | node coverage, 32768 bodies | 0.110231 | 0.0374388 | 2.94x | Same-contract node coverage remains positive. |
| Barnes-Hut / RT-BarnesHut-style | node coverage, 131072 bodies | 0.385655 | 0.304904 | 1.26x | OptiX still wins, but this is the weakest stress row. |
| Triangle counting | RT-Graph 2A1, 20000 K4 cliques | 0.101853 | 0.000703277 | 144.83x | Generic RT path remains strongly positive. |
| Triangle counting | RT-Graph 2A1, 80000 K4 cliques | 0.403863 | 0.000867688 | 465.45x | Strongest stress-row speedup. |

## Supporting Stress Rows

| App | Stress evidence | CPU/Embree sec | OptiX sec | OptiX speedup | Interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| Robot collision | 32768 poses, 512 obstacles, 2 links | 0.0568973 | 0.00643277 | 8.84x | Prepared-query stress remains strongly positive. |
| Contact manifold | grid 65536 AABB discovery + bounded collect | 36.4272 | 2.15704 | 16.89x | Large-scale contact broadphase crosses over strongly to OptiX. |
| RTNN | large prepared 3-D ranked summary, 262144 points | 3.05733 | 0.00974733 | 313.66x | Larger RTNN scale remains strongly positive. |

## Final App-by-App Verdict

| App | Final perf-diff status | Remaining boundary |
| --- | --- | --- |
| Hausdorff / X-HD-style | Finished for threshold-decision Embree-vs-OptiX diff: 2.92x, 2.10x, and 1.81x across 4096/16384/65536 copies; exact-witness OptiX rows also run. | Exact witness still lacks a same-contract Embree ratio. |
| Spatial RayJoin-style | Finished for scoped PIP, LSI, and overlay-seed diffs: 73.96x, 98.33x, and 4.77x. | Overlay row is dependency/seed contract, not full polygon overlay materialization. |
| RT-DBSCAN-style | Finished for current promoted app contract: 12.71x standard; closeout evidence also shows grouped-stream OptiX beats prepared CuPy grid by roughly 3.9-4.9x. | Embree and OptiX use different optimized routes for the same app output contract. |
| Robot collision | Finished: 5.29x standard and 8.84x prepared-query stress. | Static-scene screening only, not a planner or exact swept collision solver. |
| RayDB-style grouped aggregate | Finished for grouped count/sum: 280.15x and 249.40x. | Partner-resident CUDA grouped reduction, not RT-core traversal. |
| Barnes-Hut / RT-BarnesHut-style | Finished for same-contract node coverage: 4.56x at 8192 bodies and 3.02x at 32768 bodies. | Not full force aggregation or a full RT-BarnesHut paper reproduction. |
| LibRTS-style spatial index | Finished for count-only AABB-index contract: 29.95x. | Internal benchmark slice, not full mutable LibRTS reproduction. |
| RTNN neighbor search | Finished for uniform/clustered/shell 65536 distribution ladder: 24.29x, 23.38x, 170.63x; prior large row gives 313.66x. | Ranked-summary contract only, not official RTNN paper-system reproduction. |
| Triangle counting | Finished for synthetic RT-Graph 2A1 K4 ladder: 131.73x at 5000 cliques and 136.28x at 20000 cliques. | Paper-scale graph datasets still need segmented/streamed lowering. |
| Bounded contact witness / contact-manifold | Finished: 26.29x standard and 16.89x large contact broadphase stress. | Full contact-manifold solver remains Python/app-owned after generic AABB discovery and bounded collection. |

## Important Correction To Earlier Concern

Earlier stress artifacts showed Barnes-Hut and triangle counting losing to
Embree on larger rows. Those older losses are now explained by non-final
measurement paths:

- Barnes-Hut used process-wall and a candidate-summary/coverage mismatch before
  the same-contract node-coverage timing was stabilized.
- Triangle counting used an older fallback/process-wall path before the generic
  RT-Graph 2A1 RT-core backend-query path was stabilized.

The current fixed Goal2636 strengthened run uses the current same-contract
metrics and both apps are positive at larger standard strengthened sizes.

## Bottom Line

For the current internal benchmark portfolio, the Embree-vs-OptiX performance
diffs are now complete at the promoted exact-subpath boundaries. Every promoted
benchmark app has measured Embree/CPU and OptiX/RTDL diffs, and the additional
Goal2636 run resolves the immediate scale/workload evidence debt for the five
previously weak apps.

This still does not authorize broad public wording. The correct claim is:

```text
On the recorded RTX A5000 pod artifacts, RTDL's promoted benchmark exact
subpaths have complete Embree/CPU-vs-OptiX measurements, and the OptiX path
wins every current standard and strengthened ratio row.
```
