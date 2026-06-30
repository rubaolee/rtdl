# Goal2122 X-HD-Style Grouped Hausdorff A5000 Performance Evidence

Date: 2026-05-16

## Summary

Goal2121 added a generic OptiX point-group nearest-witness primitive and wired the v2 Hausdorff example to use X-HD-style target grouping. Goal2122 ran the new path on the A5000 pod supplied by the user:

`ssh root@69.30.85.189 -p 22108 -i id_ed25519_rtdl_codex`

GPU: NVIDIA RTX A5000, driver 570.211.01.

The result is an important partial success: the new grouped RTDL/OptiX path is slower than the exact CuPy/CUDA continuation for small and medium point sets, crosses over around 524k x 524k synthetic 2-D point sets, and is 2.21x faster at 1,048,576 x 1,048,576 while matching exact distance.

This is not yet the full X-HD paper dataset claim. The X-HD repository has run scripts and logs, but the huge input datasets are not included in the cloned repository and no direct downloader was found during this pass. The measured data here is synthetic 2-D point-set evidence shaped to stress the same exact Hausdorff computation.

## Best Observed Rows

| Points per set | Exact v2 CuPy/CUDA sec | RTDL/OptiX grouped sec | RT/CUDA ratio | Meaning |
| ---: | ---: | ---: | ---: | --- |
| 4,096 | 0.004559 | 0.073277 | 16.07x | RT slower |
| 8,192 | 0.008899 | 0.155841 | 17.51x | RT slower |
| 32,768 | 0.069233 | 0.641357 | 9.26x | RT slower |
| 65,536 | 0.238583 | 1.968912 | 8.25x | RT slower |
| 131,072 | 0.956743 | 2.649686 | 2.77x | RT slower |
| 262,144 | 3.832516 | 5.619073 | 1.47x | RT near crossover |
| 524,288 | 15.523545 | 11.643315 | 0.75x | RT 1.33x faster |
| 1,048,576 | 62.064172 | 28.076404 | 0.45x | RT 2.21x faster |

All listed grouped rows matched the exact CuPy/CUDA distance under `1e-6` tolerance.

## Interpretation

The old Goal2120 per-point AABB path was algorithmically wrong for X-HD-style performance. The grouped point-bound path changes the asymptotic behavior enough that the RT-core route eventually wins.

The crossover is still later than desired. Small and medium rows are dominated by:

- OptiX pipeline/launch overhead.
- Host-side Python grouping and row materialization.
- The current primitive returning one witness row per query, then reducing in Python.
- Lack of X-HD heavy-cell staging to cooperative CUDA blocks.
- Lack of X-HD device-side estimator state and active worklist queues.

The app-level adaptive loop was correct but did not improve timing on this synthetic distribution because it adds launches and still materializes Python rows. The next improvement should not be more Python looping; it should be a device-side generic summary primitive.

## Design Lesson

To chase the paper-level result while preserving an app-agnostic RTDL engine, the next primitive should be generic, not named Hausdorff:

`POINT_GROUP_NEAREST_MAX_DISTANCE_2D`

or more generally:

`POINT_GROUP_NEAREST_REDUCE(MAX_DISTANCE, ARGMAX_QUERY, ARGMIN_POINT)`

That primitive would:

- traverse grouped point MBRs;
- compute each query's nearest point;
- reduce max nearest-distance and witness ids on-device;
- return one scalar/witness summary instead of one Python row per query.

This maps to RTDL's existing stable primitive direction (`REDUCE_FLOAT(MAX)` plus witness ids) and keeps Hausdorff as Python app logic.

## Evidence Artifacts

- `docs/reports/goal2121_pod_grouped_hd_perf_sweep_2026-05-16.json`
- `docs/reports/goal2121_pod_grouped_adaptive_hd_perf_2026-05-16.json`
- `docs/reports/goal2121_pod_grouped_large_hd_perf_2026-05-16.json`
- `docs/reports/goal2121_pod_grouped_xlarge_hd_perf_2026-05-16.json`
- `docs/reports/goal2121_pod_grouped_million_hd_perf_2026-05-16.json`

## Verdict

- Correctness: `accept`
- Generic engine boundary: `accept`
- Large synthetic point-set RT speedup over pure CUDA/CuPy: `accept`
- Same-dataset X-HD paper claim: `needs-more-evidence`

The next work item is to add the generic on-device nearest-max summary primitive, then rerun the million-point row and any acquired X-HD paper datasets.
