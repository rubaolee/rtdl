# Goal 776: RTX 4090 One-Shot Benchmark Results

Date: 2026-04-23

## Verdict

`RTX4090_ONE_SHOT_RUN_COMPLETE_WITH_GOAL773_SCALAR_SUMMARY_EVIDENCE`

The RTX 4090 host successfully ran the Goal769 one-shot RTX benchmark pipeline from fixed commit `9a1edc1570e810f733752e06ae3fb39614c1aac1`.

This run validates that the Goal773 fixed-radius scalar-summary ABI builds and runs on real RTX hardware. It still does not authorize a broad public speedup claim; public claims require explicit baselines and independent review.

## Environment

- Cloud host: `root@213.173.111.18 -p 31613`
- Working SSH key used by Codex: `/Users/rl2025/.ssh/id_ed25519_rtdl_codex`
- GPU: `NVIDIA GeForce RTX 4090`
- Driver: `570.195.03`
- CUDA runtime reported by `nvidia-smi`: `12.8`
- CUDA toolkit used for build: `/usr/local/cuda`
- NVCC used by Goal769: `/usr/local/cuda/bin/nvcc`
- OptiX headers: `/workspace/vendor/optix-dev-9.0.0`
- Remote repo: `/workspace/rtdl_python_only`
- RTDL commit: `9a1edc1570e810f733752e06ae3fb39614c1aac1`

The provided local key `/Users/rl2025/.ssh/id_ed25519` was not present on this Mac, so Codex used `/Users/rl2025/.ssh/id_ed25519_rtdl_codex`.

## Pre-Fix Build Finding

The first RTX 4090 attempt stopped at Goal763 because Goal773 had a host/device launch-parameter mismatch. Goal775 fixed the missing host-side `threshold_reached_count` field in `FixedRadiusCountRtLaunchParams`.

No timing from the failed pre-fix attempt is used here.

## Gate Results

| Gate | Result |
|---|---:|
| SSH to RTX 4090 host | OK |
| Install/use CUDA NVCC 12.4 | OK |
| OptiX 9.0 development headers | OK |
| `make build-optix` through Goal763 | OK |
| Focused native OptiX tests | 30 tests OK |
| Goal761 manifest run | OK |
| Goal762 artifact analysis | OK |
| Artifact report failure count | 0 |
| Artifact bundle | 8 files |

## RTX 4090 Results

| App | Path | Result mode | Warm query median | Other phase evidence | Bounded interpretation |
|---|---|---:|---:|---:|---|
| `database_analytics` | prepared DB session, sales risk | prepared rows | 0.123852 s | prepared-session path, no scalar change | Valid prepared OptiX DB-session evidence; not a SQL/DBMS speedup claim. |
| `database_analytics` | prepared DB session, regional dashboard | prepared rows | 0.164188 s | prepared-session path, no scalar change | Valid prepared OptiX DB-session evidence; not a SQL/DBMS speedup claim. |
| `outlier_detection` | prepared fixed-radius density summary | `threshold_count` | 0.000443 s | input pack 0.212645 s; postprocess 0.000000 s; threshold reached 120000 / 160000 | Valid Goal773 scalar-summary evidence; not a whole anomaly-system claim. |
| `dbscan_clustering` | prepared fixed-radius core flags | `threshold_count` | 0.000451 s | input pack 0.174656 s; postprocess 0.000000 s; threshold reached 140000 / 160000 | Valid Goal773 scalar core-count evidence; not a full DBSCAN clustering claim. |
| `robot_collision_screening` | prepared pose count | `pose_count` | 0.000185 s | Python input construction 0.199082 s; scene prepare 0.729780 s; ray prepare 0.014263 s; pose-index prepare 0.000690 s; total 1.414555 s | Valid scalar pose-count evidence; not continuous collision detection or full robot kinematics. |

## Comparison Against Previous RTX 3090 Evidence

| App / path | RTX 3090 median | RTX 4090 median | Interpretation |
|---|---:|---:|---|
| DB sales risk | 0.129264 s | 0.123852 s | Similar, slightly faster on RTX 4090. |
| DB regional dashboard | 0.210792 s | 0.164188 s | Faster on RTX 4090 in this run. |
| Outlier fixed-radius summary | 0.189633 s row mode | 0.000443 s scalar mode | Not hardware-only comparison; Goal773 changed output mode and removed row materialization/postprocess. |
| DBSCAN core flags | 0.184927 s row mode | 0.000451 s scalar mode | Not hardware-only comparison; Goal773 changed output mode and removed row materialization/postprocess. |
| Robot collision | 0.000327 s pose count | 0.000185 s pose count | Same scalar-output family; RTX 4090 faster in median warm query. |

## Important Honesty Boundaries

- The RTX 4090 is real RTX-class hardware.
- Goal773 scalar fixed-radius summary builds and runs on RTX hardware after Goal775.
- The sub-millisecond fixed-radius numbers are scalar summary timings, not row-returning timings and not full Outlier/DBSCAN app timings.
- The fixed-radius comparison against RTX 3090 is not apples-to-apples because the 4090 run uses `threshold_count`, while the 3090 run used row-returning summary mode before Goal773.
- No broad public statement such as "RTDL apps are faster on RTX" is authorized from this report alone.

## Local Artifacts

- `/Users/rl2025/rtdl_python_only/docs/reports/goal769_rtx_pod_one_shot_summary_rtx4090_2026-04-23.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal762_rtx_cloud_artifact_report_rtx4090_2026-04-23.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal762_rtx_cloud_artifact_report_rtx4090_2026-04-23.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal769_rtx_pod_artifacts_rtx4090_2026-04-23.tgz`

## Next Engineering Actions

1. Ask independent review to verify the Goal776 interpretation, especially scalar-summary semantics.
2. Add explicit baselines for the same scalar outputs before public speedup language.
3. Keep optimizing Python/setup phases because native warm query time is now much smaller than input construction and scene preparation.
