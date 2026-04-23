# Goal 772: RTX 3090 One-Shot Benchmark Results

Date: 2026-04-23

## Verdict

`RTX3090_ONE_SHOT_RUN_COMPLETE_WITH_BOUNDED_INTERNAL_EVIDENCE`

The new RunPod-style RTX 3090 host successfully ran the Goal769 one-shot RTX benchmark pipeline on branch `codex/rtx-cloud-run-2026-04-22` at commit `cb752c09bef24338321ddea3787c5bc877da1566`.

This is valid RTX-class hardware evidence for the selected RTDL OptiX app paths. It does not authorize a broad public RTX speedup claim. Public claims still require explicit baselines, independent review, and separate treatment of native traversal time versus Python/application overhead.

## Environment

- Cloud host: `root@213.192.2.86 -p 40185`
- Working SSH key used by Codex: `/Users/rl2025/.ssh/id_ed25519_rtdl_codex`
- GPU: `NVIDIA GeForce RTX 3090`
- Driver: `580.126.20`
- CUDA runtime reported by `nvidia-smi`: `13.0`
- CUDA toolkit used for build: `/usr/local/cuda`
- NVCC used by Goal769: `/usr/local/cuda/bin/nvcc`
- OptiX headers: `/workspace/vendor/optix-dev-9.0.0`
- OptiX source: NVIDIA `optix-dev` tag `v9.0.0`
- Remote repo: `/workspace/rtdl_python_only`

The originally suggested local key `/Users/rl2025/.ssh/id_ed25519` was not present on this Mac. The older project key `/Users/rl2025/.ssh/id_ed25519_rtdl_codex` worked and was used for the run.

## Execution Command

```bash
cd /workspace/rtdl_python_only
export PATH=/usr/local/cuda-12.4/bin:/usr/local/cuda/bin:$PATH
export CUDA_PREFIX=/usr/local/cuda
export NVCC=/usr/local/cuda-12.4/bin/nvcc
PYTHONPATH=src:. python3 scripts/goal769_rtx_pod_one_shot.py \
  --optix-prefix /workspace/vendor/optix-dev-9.0.0 \
  --output-json docs/reports/goal769_rtx_pod_one_shot_summary_rtx3090_2026-04-23.json \
  --artifact-json docs/reports/goal762_rtx_cloud_artifact_report_rtx3090_2026-04-23.json \
  --artifact-md docs/reports/goal762_rtx_cloud_artifact_report_rtx3090_2026-04-23.md \
  --bundle-tgz docs/reports/goal769_rtx_pod_artifacts_rtx3090_2026-04-23.tgz
```

## Gate Results

| Gate | Result |
|---|---:|
| SSH with old project key | OK |
| CUDA/NVCC setup | OK |
| OptiX 9.0 development headers | OK |
| `make build-optix` through Goal763 | OK |
| Focused native OptiX tests | 29 tests OK |
| Goal761 manifest run | OK |
| Goal762 artifact analysis | OK |
| Artifact report failure count | 0 |

## RTX 3090 Results

| App | Path | Scale / scope | Warm query median | Other phase evidence | Bounded interpretation |
|---|---|---:|---:|---:|---|
| `database_analytics` | prepared DB session, sales risk | prepared OptiX DB session | 0.129264 s | prepare total 0.585884 s; one-shot total 1.903282 s | Valid prepared-session OptiX evidence; not a SQL engine or broad DBMS speedup claim. |
| `database_analytics` | prepared DB session, regional dashboard | prepared OptiX DB session | 0.210792 s | prepare total 0.741265 s; one-shot total 2.024602 s | Valid prepared-session OptiX evidence; Python/result and query semantics remain separately bounded. |
| `outlier_detection` | prepared fixed-radius density summary | fixed-radius threshold summary | 0.189633 s | input pack 0.260237 s; postprocess median 0.113743 s; one-shot total 2.190670 s | Valid prepared fixed-radius summary evidence after packed-point reuse; not a full anomaly-system claim. |
| `dbscan_clustering` | prepared fixed-radius core flags | DBSCAN core-flag summary only | 0.184927 s | input pack 0.246226 s; postprocess median 0.114049 s; one-shot total 1.214739 s | Valid core-flag traversal evidence; not a full DBSCAN clustering speedup claim. |
| `robot_collision_screening` | prepared pose count | 200k poses, 800k edge rays, 2048 obstacle triangles | 0.000327 s | Python input construction 2.561149 s; scene prepare 1.101614 s; ray prepare 0.019577 s; pose-index prepare 0.000968 s; total 4.385253 s | Strong native scalar-output evidence, but not apples-to-apples with earlier pose-flag output. Needs review before public use. |

## Comparison Against Previous RTX A5000 Evidence

| App / path | RTX A5000 prior median | RTX 3090 median | Interpretation |
|---|---:|---:|---|
| DB sales risk | 0.137131 s | 0.129264 s | Slightly faster on RTX 3090. |
| DB regional dashboard | 0.204094 s | 0.210792 s | Similar; slightly slower on this run. |
| Outlier fixed-radius summary | 0.490954 s | 0.189633 s | Faster after Goal770 packed-query reuse; not a pure GPU-to-GPU hardware comparison. |
| DBSCAN core flags | 0.482424 s | 0.184927 s | Faster after Goal770 packed-query reuse; not a pure GPU-to-GPU hardware comparison. |
| Robot collision | 0.240423 s pose flags | 0.000327 s pose count | New scalar-output ABI, not comparable to the earlier flag-buffer output path. |

## Important Honesty Boundaries

- The RTX 3090 is real RTX-class hardware, and the OptiX backend built and passed focused native tests on it.
- The manifest completed all five app entries with `failure_count: 0`.
- The robot scalar pose-count number is promising but must be reviewed carefully because it changes result materialization from per-pose flags to one scalar count.
- The fixed-radius gains include a code-path improvement from Goal770, so they should be described as post-optimization results, not only as an RTX 3090 hardware effect.
- No broad public statement such as "RTDL apps are faster on RTX" is authorized from this report alone.

## Local Artifacts

- `/Users/rl2025/rtdl_python_only/docs/reports/goal769_rtx_pod_one_shot_summary_rtx3090_2026-04-23.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal762_rtx_cloud_artifact_report_rtx3090_2026-04-23.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal762_rtx_cloud_artifact_report_rtx3090_2026-04-23.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal769_rtx_pod_artifacts_rtx3090_2026-04-23.tgz`

## Next Engineering Actions

1. Ask an independent AI reviewer to validate the Goal772 artifact interpretation before public documentation uses these numbers.
2. Add explicit baselines for each app path before making any speedup claim.
3. Continue reducing Python and result-materialization overhead on the robot and fixed-radius paths, because the native traversal portions are now much smaller than the surrounding application phases.
