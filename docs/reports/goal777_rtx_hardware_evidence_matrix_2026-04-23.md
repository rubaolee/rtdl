# Goal 777: RTX Hardware Evidence Matrix

Date: 2026-04-23

## Verdict

`INTERNAL_MULTI_GPU_EVIDENCE_CONSOLIDATED`

RTDL now has successful one-shot OptiX benchmark evidence on three RTX-class cloud GPUs:

- NVIDIA RTX A5000
- NVIDIA GeForce RTX 3090
- NVIDIA GeForce RTX 4090

All three runs completed the RTX manifest with artifact `failure_count: 0`. The runs are not all apples-to-apples because the code path evolved between them. This report is therefore an internal engineering evidence matrix, not a public speedup table.

## Source Artifacts

| GPU | Artifact report | Commit | Status |
|---|---|---:|---:|
| RTX A5000 | `/Users/rl2025/rtdl_python_only/docs/reports/goal762_rtx_cloud_artifact_report_runpod_2026-04-23.json` | `e74c54e89e3548627b69b24a73d36870b7b6d08e` | OK |
| RTX 3090 | `/Users/rl2025/rtdl_python_only/docs/reports/goal762_rtx_cloud_artifact_report_rtx3090_2026-04-23.json` | `cb752c09bef24338321ddea3787c5bc877da1566` | OK |
| RTX 4090 | `/Users/rl2025/rtdl_python_only/docs/reports/goal762_rtx_cloud_artifact_report_rtx4090_2026-04-23.json` | `9a1edc1570e810f733752e06ae3fb39614c1aac1` | OK |

## Hardware

| GPU | Driver | CUDA reported by `nvidia-smi` | Notes |
|---|---:|---:|---|
| RTX A5000 | `580.126.09` | CUDA 13-class runtime display on that host | First successful RTX-class cloud run after OptiX 9.0 header correction. |
| RTX 3090 | `580.126.20` | `13.0` | First successful run after Goals766-770 and Goal769 packaging. |
| RTX 4090 | `570.195.03` | `12.8` | First successful run after Goal773 scalar fixed-radius summary and Goal775 build fix. |

## Warm Query Medians

| App path | RTX A5000 | RTX 3090 | RTX 4090 | Interpretation |
|---|---:|---:|---:|---|
| DB sales risk prepared session | 0.137131 s | 0.129264 s | 0.123852 s | Comparable prepared DB-session family; 4090 is modestly faster in this matrix. |
| DB regional dashboard prepared session | 0.204094 s | 0.210792 s | 0.164188 s | Comparable prepared DB-session family; 4090 is faster than both earlier runs here. |
| Outlier fixed-radius summary | 0.490954 s | 0.189633 s | 0.000443 s | Not apples-to-apples: A5000 was row-returning; 3090 had packed-point reuse; 4090 uses Goal773 scalar `threshold_count`. |
| DBSCAN core flags | 0.482424 s | 0.184927 s | 0.000451 s | Not apples-to-apples for the same reason as Outlier. |
| Robot collision | 0.240423 s pose flags | 0.000327 s pose count | 0.000185 s pose count | 3090 and 4090 are scalar pose-count; A5000 was earlier per-pose flag output. |

## Setup / App Phase Evidence

| App path | RTX 3090 setup/postprocess | RTX 4090 setup/postprocess | Interpretation |
|---|---:|---:|---|
| Outlier fixed-radius summary | pack 0.260237 s; postprocess 0.113743 s | pack 0.212645 s; postprocess 0.000000 s | Goal773 removed row postprocess from the scalar summary path. |
| DBSCAN core flags | pack 0.246226 s; postprocess 0.114049 s | pack 0.174656 s; postprocess 0.000000 s | Goal773 removed row postprocess from the scalar core-count path. |
| Robot collision | pose-index prepare 0.000968 s | pose-index prepare 0.000690 s | Same scalar-output family on 3090 and 4090; 4090 run is faster in median warm query. |

## Honest Conclusions

1. RTDL's selected OptiX paths build and run on multiple real RTX-class GPUs.
2. The DB prepared-session path is stable across A5000, 3090, and 4090, with 4090 showing the best observed medians in this set.
3. The large fixed-radius improvement in the 4090 run is primarily a code-path improvement from Goal773, not a pure GPU hardware effect.
4. The robot scalar pose-count path is now a strong native-summary candidate: 4090 median `0.000185 s` for the prepared warm query on 200k poses / 800k edge rays / 2048 obstacle triangles.
5. App-level time can still be dominated by setup, input construction, scene preparation, and Python orchestration, so public claims must keep native traversal and whole-app timing separate.

## Not Allowed From This Matrix

- Do not claim "RTDL apps are faster on RTX" broadly.
- Do not compare A5000 row-returning fixed-radius results directly to 4090 scalar fixed-radius results as if only the GPU changed.
- Do not claim full Outlier, full DBSCAN clustering, SQL/DBMS, continuous collision detection, or full robot kinematics acceleration.
- Do not publish the sub-millisecond scalar timings without explaining that they are scalar-summary prepared warm-query timings.

## Next

For future dynamic cloud GPU availability:

- Any RTX 4090, RTX 3090, RTX A5000, L4, L40S, A10, A40, or T4 host can be run through the same Goal769 one-shot pipeline.
- Each new GPU should be recorded as a new hardware row, not merged into a single broad claim.
- The next best measurement target is an L4 run if available, because it is a common cloud Ada GPU and will help readers understand modern datacenter RTX behavior.
