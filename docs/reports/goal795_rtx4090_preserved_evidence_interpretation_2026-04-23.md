# Goal795 RTX 4090 Preserved Evidence Interpretation

Date: 2026-04-23

## Verdict

Status: `evidence preserved, claims still bounded`.

The stopped RTX 4090 pod produced useful NVIDIA/OptiX evidence. The evidence is strong enough to keep the cloud-derived fixes and continue local development, but it is not yet enough for broad public RTX speedup claims.

## Source Artifacts

- Replay log: `/Users/rl2025/rtdl_python_only/docs/reports/goal790_rtx4090_cloud_replay_log_2026-04-23.md`
- Final follow-up raw result: `/Users/rl2025/rtdl_python_only/docs/reports/goal793_rtx4090_rtx_only_followup_2026-04-23.json`
- Final follow-up artifact summary: `/Users/rl2025/rtdl_python_only/docs/reports/goal793_rtx_cloud_artifact_report_rtx4090_latest_2026-04-23.md`
- Machine-readable artifact summary: `/Users/rl2025/rtdl_python_only/docs/reports/goal793_rtx_cloud_artifact_report_rtx4090_latest_2026-04-23.json`

## Hardware And Environment

| Field | Value |
|---|---|
| GPU | NVIDIA GeForce RTX 4090 |
| Driver | 570.195.03 |
| CUDA reported by `nvidia-smi` | 12.8 |
| Artifact git head | `259c0c2dcdda373c8003cf3409a387ab61c5f407` |
| Runner status | `ok` |
| Failure count | `0` |

## Preserved App-Path Timings

These are preserved phase timings from the final RTX-only follow-up. They are not whole-application public speedup claims.

| App | RTDL path | Prepare / pack phase | Warm native query median | Native result mode | Result summary | Correct interpretation |
|---|---|---:|---:|---|---|---|
| Database analytics | prepared DB session, sales risk | prepare total `0.257902s` | `0.090205s` | prepared query | one-shot / warm ratio `11.51x` | Evidence for repeated prepared OptiX DB-session behavior and phase split, not SQL-engine superiority. |
| Database analytics | prepared DB session, regional dashboard | prepare total `0.329046s` | `0.145297s` | prepared query | one-shot / warm ratio `7.66x` | Evidence for repeated prepared OptiX DB-session behavior and phase split, not SQL-engine superiority. |
| Outlier detection | prepared fixed-radius density summary | pack `0.138852s`, prepare `0.593074s` | `0.000409s` | `threshold_count` | count `120000` | Evidence for native prepared scalar fixed-radius summary only, not full anomaly-detection app speedup. |
| DBSCAN clustering | prepared fixed-radius core flags | pack `0.121584s`, prepare `0.002743s` | `0.000405s` | `threshold_count` | count `140000` | Evidence for native prepared scalar core-flag summary only, not full DBSCAN clustering speedup. |
| Robot collision screening | prepared pose flags | pose-index prepare `0.000523s` | `0.000179s` | `pose_count` | count `193750` | Evidence for native prepared scalar pose-count traversal only, not full robot kinematics or CCD replacement. |

## What The RTX Session Proved

1. The OptiX 2D point ABI bug was real and is fixed.
2. The correct cloud OptiX environment must set both `NVCC` and `RTDL_NVCC`; `NVCC` alone is insufficient for RTDL native PTX fallback.
3. The final RTX-only follow-up can build OptiX, pass focused OptiX regression checks, pass public-doc/report-smoke follow-up, and run the official one-shot path.
4. Prepared scalar-output paths can keep warm native query phases very small on RTX 4090 once Python row materialization is removed from the timed phase.

## What The RTX Session Did Not Prove

1. It did not prove broad whole-app speedup over mature libraries.
2. It did not prove that row-returning fixed-radius, KNN, Hausdorff, ANN, or Barnes-Hut paths are fully optimized RT-core applications.
3. It did not prove SQL/database superiority; the DB evidence is an RTDL prepared-session phase split.
4. It did not make Embree cloud evidence relevant; Embree is CPU-only and should be tested on local CPU machines.

## Next Optimization Queue Before Another Pod

1. Convert more app paths from Python row materialization to native scalar or compact-buffer outputs where the app only needs counts, flags, minima, maxima, or top-k candidates.
2. Add per-app baseline scripts that separate prepare, transfer, native query, and Python postprocess phases before any new cloud run.
3. Keep the cloud runner batched and replayable; do not rent GPU time for one isolated command.
4. For the next NVIDIA pod, run only after local changes are ready and collect one batch covering OptiX, Vulkan, HIPRT-on-NVIDIA if relevant, and public smoke checks.

## Release Claim Boundary

Allowed internal claim: selected prepared RTDL OptiX paths build and run on real RTX 4090 hardware with preserved phase artifacts, and the strongest native prepared scalar phases are sub-millisecond in this run.

Disallowed public claim: RTDL apps broadly beat existing systems or mature libraries on RTX hardware. That requires reviewed baselines, repeated runs, and app-level phase accounting.
