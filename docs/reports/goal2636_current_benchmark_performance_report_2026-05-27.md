# Goal2636 Current Benchmark Performance Report

Date: 2026-05-27

Status: internal measured-performance report. This is not public speedup
wording.

Superseded for all-benchmark perf diffs by
`docs/reports/goal2637_all_benchmark_perf_diffs_2026-05-27.md`, which includes
the fixed-environment Goal2636 pod run.

## Source Of Truth

This report uses measured artifacts already copied into the repository. It does
not use dry-run output from the new Goal2636 strengthening runner as
performance evidence.

Primary measured artifact:

- `docs/reports/goal2634_full_standard_prepared_contact_pod/summary.md`
- `docs/reports/goal2634_full_standard_prepared_contact_pod/summary_slim.json`

Supporting interpretation:

- `docs/reports/goal2634_gap_closure_and_rt_baseline_2026-05-27.md`
- `docs/reports/goal2626_benchmark_embree_optix_stress_addendum_2026-05-26.md`
- `docs/reports/goal2635_benchmark_app_optimization_validity_audit_2026-05-27.md`
- `docs/reports/goal2636_strengthened_benchmark_rows_plan_2026-05-27.md`

Measured environment for the primary matrix:

| Item | Value |
| --- | --- |
| Pod | `root@203.57.40.101 -p 10165` |
| GPU | NVIDIA RTX A5000, driver 565.57.01, 24564 MiB |
| Commit | `56e1f9b230cdef6d803191c8804f192133b4d020` |
| Command | `PYTHONPATH=src:. python3 scripts/goal2626_benchmark_embree_optix_baseline.py --scale standard --artifact-dir /root/rtdl_goal2634_full_standard_prepared_contact --timeout-sec 1200` |

## Main Result

The current standard matrix covers 10 promoted benchmark apps and 11 comparison
rows, because RayDB-style grouped aggregate has separate grouped-count and
grouped-sum contracts.

For the recorded standard primary metrics:

| Metric | Value |
| --- | ---: |
| Rows where OptiX/RTDL path is faster than Embree/CPU path | 11 / 11 |
| Minimum OptiX speedup | 3.29x |
| Median OptiX speedup | 29.95x |
| Geometric-mean OptiX speedup | 32.25x |
| Maximum OptiX speedup | 280.15x |

This supports a narrow internal conclusion:

```text
For the current promoted benchmark suite's recorded standard exact-subpath
metrics, every row has both Embree/CPU and OptiX entries, and the OptiX/RTDL
path is faster on every recorded primary metric.
```

It does not support a broad public conclusion that RTDL always beats Embree,
that every app is fully paper-scale, or that the standard row is representative
of every workload size.

## Standard Matrix

| App | Comparison group | Embree sec | OptiX sec | OptiX speedup | Current trust level |
| --- | --- | ---: | ---: | ---: | --- |
| Hausdorff / X-HD-style | threshold decision | 0.102451 | 0.0311073 | 3.29x | Valid exact subpath; needs larger threshold/witness ladder. |
| Spatial RayJoin-style | all-backend scoped query summary | 0.0203149 | 0.000529638 | 38.36x | Valid scoped route; fixture is too small and needs nonzero tiled all-route coverage. |
| RT-DBSCAN-style | cluster signature | 20.6102 | 1.62144 | 12.71x | Strong current app-contract baseline; not pure backend-only microcomparison. |
| Robot collision | prepared collision flags | 0.00853798 | 0.00161413 | 5.29x | Strong prepared-query baseline; do not include CPU oracle/process-wall in speedup wording. |
| RayDB-style grouped aggregate | grouped count | 0.222185 | 0.000793088 | 280.15x | Strong grouped-reduction subpath; not an RT-core acceleration claim. |
| RayDB-style grouped aggregate | grouped sum | 0.243746 | 0.000977349 | 249.40x | Strong grouped-reduction subpath; not an RT-core acceleration claim. |
| Barnes-Hut / RT-BarnesHut-style | node coverage prepared threshold decision | 0.0388851 | 0.00855045 | 4.55x | Valid node-coverage subpath; not full force aggregation and needs scale ladder. |
| LibRTS-style spatial index | AABB index all count-only | 20.7070 | 0.691477 | 29.95x | Strong count-only AABB-index contract; Embree row is CPU-fallback-like app contract. |
| RTNN neighbor search | prepared 3-D ranked summary | 0.263800 | 0.00153247 | 172.14x | Valid ranked-summary contract; needs distribution and density ladder. |
| Triangle counting | RT-Graph-style RT-2A1 summary | 0.0390490 | 0.000364401 | 107.16x | Valid synthetic backend-query subpath; not paper-dataset scale. |
| Bounded contact witness / contact-manifold | generic AABB broadphase + bounded collection | 0.485812 | 0.0184764 | 26.29x | Strong generic AABB row discovery + bounded collection baseline. |

## Stress Evidence Already Known

The stress addendum is important because it prevents overclaiming. It shows
that some standard-row wins do not automatically survive larger or different
workloads.

| Stress test | Scale | Embree or CPU sec | OptiX sec | OptiX speedup | Interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| Hausdorff / X-HD threshold | 16384 copies | 0.399736 | 0.370397 | 1.08x | OptiX still wins, but the margin nearly disappears. |
| Barnes-Hut node coverage | 32768 bodies | 0.949983 | 1.76206 | 0.539x | Embree wins on this older large row; current same-contract ladder must be rerun. |
| Triangle counting summary | 20000 copies | 0.915364 | 1.56583 | 0.585x | Embree wins on this older large row; synthetic standard row is not enough. |
| Robot collision prepared query | 32768 poses, 512 obstacles, 2 links | 0.0568973 | 0.00643277 | 8.84x | OptiX wins in steady-state prepared-query timing. |
| Contact AABB collect | grid 8192 | 0.837436 | 0.929862 | 0.901x | Small-scale overhead can favor CPU. |
| Contact AABB collect | grid 65536 | 36.4272 | 2.15704 | 16.9x | Larger scale crosses over strongly to OptiX. |

## App-Level Verdict

| Class | Apps | Verdict |
| --- | --- | --- |
| Strong current benchmark evidence | RT-DBSCAN, robot collision, RayDB grouped count/sum, LibRTS spatial index, contact manifold | Current optimized path is represented in the measured matrix. Claim boundary remains exact-subpath and internal. |
| Needs stronger workload coverage before broad RT-vs-Embree conclusion | Hausdorff, Spatial RayJoin, RTNN, Barnes-Hut, triangle counting | Current standard rows are valid, but scale/workload coverage is not strong enough. Goal2636 exists to rerun these rows with larger ladders. |
| Not an RT-core speedup claim | RayDB grouped count/sum | The OptiX-labeled row uses partner-resident CUDA grouped reduction. It is valuable for Python+partner+RTDL, but should not be counted as RT-core traversal evidence. |

## What The Performance Data Actually Says

The strongest positive signal is that the app-agnostic RTDL primitive strategy
is working for multiple distinct benchmark shapes:

- fixed-radius/grouped continuation: RT-DBSCAN and RTNN;
- prepared any-hit/flag queries: robot collision;
- AABB index/query rows: LibRTS and contact manifold;
- typed partner-resident grouped reductions: RayDB;
- RT-shaped graph and spatial query subpaths: triangle counting and RayJoin;
- aggregate/frontier-adjacent coverage queries: Barnes-Hut;
- thresholded nearest/coverage decisions: Hausdorff.

The main weakness is measurement maturity, not just implementation maturity.
Several apps already have a valid OptiX path, but the standard matrix does not
yet prove the result is stable across realistic scale ladders. The strongest
example is Barnes-Hut and triangle counting: both standard rows are OptiX wins,
but older stress rows show Embree wins at larger scale. Those apps require a
fresh current-main scale ladder before any serious broad claim.

## Required Next Measurement

The next serious performance step is to run the Goal2636 standard tier on a pod:

```bash
PYTHONPATH=src:. python3 scripts/goal2636_strengthen_benchmark_rows.py \
  --tier standard \
  --artifact-dir docs/reports/goal2636_strengthened_rows_pod \
  --timeout-sec 1800 \
  --build-native
```

If the standard tier is stable:

```bash
PYTHONPATH=src:. python3 scripts/goal2636_strengthen_benchmark_rows.py \
  --tier stress \
  --artifact-dir docs/reports/goal2636_strengthened_rows_stress_pod \
  --timeout-sec 3600 \
  --build-native
```

The output from those commands is required before changing this report from
"current measured baseline plus known gaps" to "strengthened performance
baseline."

## Bottom Line

The current measured performance is good enough for an internal v2.x baseline:
all 11 standard rows are positive, with a median 29.95x and geometric-mean
32.25x OptiX advantage on the recorded exact subpaths.

It is not yet good enough for a broad "RT beats Embree" claim across the whole
benchmark portfolio. Hausdorff, Spatial RayJoin, RTNN, Barnes-Hut, and triangle
counting still need the Goal2636 larger workload run. Barnes-Hut and triangle
counting especially must be treated carefully because existing stress evidence
already shows Embree can win on older larger rows.
