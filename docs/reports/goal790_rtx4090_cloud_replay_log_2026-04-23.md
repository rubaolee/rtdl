# Goal 790 RTX 4090 Cloud Replay Log

Date: 2026-04-23

Pod:

- SSH: `root@213.173.111.18 -p 31613`
- Key used locally: `/Users/rl2025/.ssh/id_ed25519_rtdl_codex`
- Hostname: `aa4e4f169c85`
- GPU: NVIDIA GeForce RTX 4090, 24564 MiB
- Driver: `570.195.03`
- CUDA runtime reported by `nvidia-smi`: `12.8`
- CUDA compiler used: `/usr/local/cuda-12.4/bin/nvcc`
- OptiX headers used: `/workspace/vendor/optix-dev-9.0.0`

## Operational Rule

The pod was already running, so the work was batched in-place. The pod was not
stopped or restarted between these checks. Every remote batch wrote a JSON
artifact under:

- `/workspace/rtdl_python_only/docs/reports/`

The same artifacts were pulled back to:

- `/Users/rl2025/rtdl_python_only/docs/reports/`

## Environment Commands

The successful OptiX runs used the following required environment shape:

```bash
export PYTHONPATH=src:.
export PATH=/usr/local/cuda-12.4/bin:/usr/local/cuda/bin:$PATH
export CUDA_PREFIX=/usr/local/cuda
export NVCC=/usr/local/cuda-12.4/bin/nvcc
export RTDL_NVCC=/usr/local/cuda-12.4/bin/nvcc
export OPTIX_PREFIX=/workspace/vendor/optix-dev-9.0.0
export RTDL_OPTIX_LIB=/workspace/rtdl_python_only/build/librtdl_optix.so
export RTDL_OPTIX_PTX_COMPILER=nvcc
```

Important: `RTDL_NVCC` is required by the native OptiX PTX fallback path. Setting
only `NVCC` is not enough.

## Raw Artifact Index

| Goal | Artifact | Purpose | Result |
| --- | --- | --- | --- |
| 778 | `/Users/rl2025/rtdl_python_only/docs/reports/goal778_rtx4090_extra_gpu_backend_batch_2026-04-23.json` | First broad OptiX/Vulkan/HIPRT batch | Diagnostic only; stale pod workspace and missing prefixes exposed |
| 779 | `/Users/rl2025/rtdl_python_only/docs/reports/goal779_rtx4090_optix_corrected_batch_2026-04-23.json` | Corrected OptiX SDK prefix | Build passed; NVRTC system-header issue exposed |
| 780 | `/Users/rl2025/rtdl_python_only/docs/reports/goal780_rtx4090_optix_after_libc_i386_2026-04-23.json` | Installed `libc6-dev-i386` and reran | Header issue fixed; unsafe NVRTC launch issue exposed |
| 781 | `/Users/rl2025/rtdl_python_only/docs/reports/goal781_rtx4090_optix_nvrtc_fixed_2026-04-23.json` | Tried NVRTC default-device option | Rejected; caused invalid OptiX launch parameters |
| 782 | `/Users/rl2025/rtdl_python_only/docs/reports/goal782_rtx4090_optix_nvcc_batch_2026-04-23.json` | Reverted unsafe NVRTC option and forced nvcc | Still incomplete because `RTDL_NVCC` was missing |
| 783 | `/Users/rl2025/rtdl_python_only/docs/reports/goal783_rtx4090_optix_runbook_env_2026-04-23.json` | Full runbook env with `RTDL_NVCC` | Scalar fixed-radius and robot perf passed; legacy 2D OptiX row tests failed |
| 784 | `/Users/rl2025/rtdl_python_only/docs/reports/goal784_rtx4090_optix_legacy_isolation_2026-04-23.json` | Isolated legacy fixed-radius/KNN row tests | Confirmed real correctness bug independent of NVRTC vs nvcc |
| 785 | `/Users/rl2025/rtdl_python_only/docs/reports/goal785_rtx4090_optix_padding_fix_2026-04-23.json` | Verified the 2D point ABI padding fix | PASS: legacy tests, broader OptiX suite, scalar perf, and robot perf |
| 786 | `/Users/rl2025/rtdl_python_only/docs/reports/goal786_rtx4090_more_gpu_checks_2026-04-23.json` | Extra Vulkan/package probe and focused tests | Diagnostic only; harness argument and test-name mistakes logged |
| 787 | `/Users/rl2025/rtdl_python_only/docs/reports/goal787_rtx4090_corrected_official_checks_2026-04-23.json` | Corrected focused tests and one-shot rerun | Focused tests passed; one-shot default OptiX prefix was wrong |
| 788 | `/Users/rl2025/rtdl_python_only/docs/reports/goal788_rtx4090_official_with_prefix_2026-04-23.json` | Official one-shot with explicit OptiX prefix | PASS |
| 789 | `/Users/rl2025/rtdl_python_only/docs/reports/goal789_rtx4090_full_discovery_2026-04-23.json` | Broad Linux RTX full unittest discovery | FAILED: non-OptiX environment/doc failures remain |

## Code Fixes Produced

### Rejected Fix

Commit `38adbb1` added `--device-as-default-execution-space` to the shared
OptiX NVRTC path. This made NVRTC compilation progress but caused invalid OptiX
launch parameters. It was reverted by commit `b99616d`.

### Accepted Fix

Commit `9808e81` fixed a real 2D OptiX ABI bug:

- Host-side `GpuPt` for 2D fixed-radius rows and KNN rows was 12 bytes:
  `float x, y; uint32_t id`.
- Device-side kernels expected 16 bytes:
  `float x, y; uint32_t id; uint32_t pad`.
- On RTX 4090 this caused wrong IDs, missing neighbor rows, and KNN corruption.
- The host-side structs now include the padding field and initialize it to `0u`.

## Final Passing RTX 4090 Evidence

The final successful focused backend check is:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal785_rtx4090_optix_padding_fix_2026-04-23.json`

It records:

- `build_optix`: PASS
- `legacy_216_217_correctness`: PASS
- `optix_extended_correctness`: PASS
- `optix_fixed_radius_scalar_100k`: PASS
- `optix_robot_pose_count_1000k`: PASS

The final successful official one-shot is:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal788_rtx4090_official_with_prefix_2026-04-23.json`

It records:

- official one-shot return code `0`
- branch commit `9808e81d2061ba3f6e413c4bdaa089ff3fd08d5c`
- artifact report:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal788_rtx_cloud_artifact_report_rtx4090_fixed_2026-04-23.json`
- markdown artifact report:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal788_rtx_cloud_artifact_report_rtx4090_fixed_2026-04-23.md`
- bundle:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal788_rtx_pod_artifacts_rtx4090_fixed_2026-04-23.tgz`

## Key Performance Numbers

From `/Users/rl2025/rtdl_python_only/docs/reports/goal785_rtx4090_fixed_radius_scalar_100k_2026-04-23.json`:

| App | Scale | Result Mode | Warm Query Median |
| --- | ---: | --- | ---: |
| Outlier detection | 800,000 points | `threshold_count` | `0.002407885s` |
| DBSCAN core flags | 800,000 points | `threshold_count` | `0.002031713s` |

From `/Users/rl2025/rtdl_python_only/docs/reports/goal785_rtx4090_robot_pose_count_1000k_2026-04-23.json`:

| App | Scale | Result Mode | Warm Query Median |
| --- | ---: | --- | ---: |
| Robot collision screening | 1,000,000 poses, 4,000,000 edge rays, 8,192 obstacle triangles | `pose_count` | `0.000803944s` |

These are prepared native summary-path phase timings. They are not whole-app
speedup claims and do not include Python input construction, full row
materialization, or external baseline comparisons.

## Vulkan And HIPRT Notes

Vulkan was probed but not validated on this pod:

- `vulkaninfo --summary` reported `ERROR_INCOMPATIBLE_DRIVER`.
- `make build-vulkan` failed because `shaderc/shaderc.h` was not present.
- `apt-cache`/package probing was recorded in Goal786.

HIPRT was probed but not validated on this pod:

- `make build-hiprt` failed because the HIPRT SDK header was not present at the
  expected path.
- HIPRT unit-test invocations in the broad batch returned quickly because the
  native HIPRT library was unavailable.

These are environment/setup limitations for this pod image, not correctness
evidence for Vulkan or HIPRT.

## Full Discovery Result

The broad Linux RTX full discovery artifact is:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal789_rtx4090_full_discovery_2026-04-23.json`

It ran:

```bash
python3 -m unittest discover -s tests -p "*_test.py" -v
```

Result:

- `1479` tests discovered/run
- `298` skips
- exit code `1`
- failures/errors were outside the final focused RTX OptiX slice

Known categories from the captured tail:

- Embree auto-build failed on the pod because `-lembree4` was unavailable.
- Public doc consistency tests found stale/concision issues:
  `goal527_examples_capability_boundary_refresh_test` and
  `goal646_public_front_page_doc_consistency_test`.

This means the pod is now good RTX OptiX evidence, but not a clean full-release
Linux environment until Embree dependencies and public docs are fixed.

## Replay Order

To replay the successful final path from a clean pod:

1. Clone branch `codex/rtx-cloud-run-2026-04-22`.
2. Install CUDA compiler and OptiX headers.
3. Ensure the environment block above is set, especially `RTDL_NVCC`.
4. Build:

```bash
make build-optix OPTIX_PREFIX=/workspace/vendor/optix-dev-9.0.0 CUDA_PREFIX=/usr/local/cuda NVCC=/usr/local/cuda-12.4/bin/nvcc
```

5. Run focused correctness:

```bash
python3 -m unittest -v \
  tests.goal216_fixed_radius_neighbors_optix_test \
  tests.goal217_knn_rows_optix_test \
  tests.goal43_optix_validation_test \
  tests.goal45_optix_county_zipcode_test \
  tests.goal47_optix_goal41_large_checks_test \
  tests.goal110_segment_polygon_hitcount_closure_test \
  tests.goal311_v0_5_optix_3d_nn_test \
  tests.goal394_v0_6_rt_graph_bfs_optix_test \
  tests.goal397_v0_6_rt_graph_triangle_optix_test \
  tests.goal427_v0_7_rt_db_optix_backend_test \
  tests.goal435_v0_7_optix_native_prepared_db_dataset_test \
  tests.goal637_optix_native_any_hit_test \
  tests.goal671_optix_prepared_anyhit_count_test \
  tests.goal757_prepared_optix_fixed_radius_count_test
```

6. Run focused performance:

```bash
python3 scripts/goal757_optix_fixed_radius_prepared_perf.py \
  --copies 100000 \
  --iterations 8 \
  --result-mode threshold_count \
  --skip-validation \
  --output-json docs/reports/goal785_rtx4090_fixed_radius_scalar_100k_2026-04-23.json

python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py \
  --mode optix \
  --pose-count 1000000 \
  --obstacle-count 4096 \
  --iterations 8 \
  --input-mode packed_arrays \
  --result-mode pose_count \
  --skip-validation \
  --output-json docs/reports/goal785_rtx4090_robot_pose_count_1000k_2026-04-23.json
```

7. Run official one-shot:

```bash
python3 scripts/goal769_rtx_pod_one_shot.py \
  --branch codex/rtx-cloud-run-2026-04-22 \
  --optix-prefix /workspace/vendor/optix-dev-9.0.0 \
  --skip-git-update \
  --skip-optix-install \
  --output-json docs/reports/goal788_rtx_pod_one_shot_summary_rtx4090_fixed_2026-04-23.json \
  --artifact-json docs/reports/goal788_rtx_cloud_artifact_report_rtx4090_fixed_2026-04-23.json \
  --artifact-md docs/reports/goal788_rtx_cloud_artifact_report_rtx4090_fixed_2026-04-23.md \
  --bundle-tgz docs/reports/goal788_rtx_pod_artifacts_rtx4090_fixed_2026-04-23.tgz
```

## Current Release Implication

The RTX OptiX app-performance path is stronger after this work because an
actual cloud-only 2D ABI bug was found and fixed. However, this does not close a
full release gate by itself. Remaining work before using this as release-level
evidence:

- fix or explicitly scope the full-discovery Embree dependency issue on the pod;
- fix the public docs tests found by Goal789;
- obtain independent review of this replay log and the Goal785/Goal788
  artifacts before making public performance claims.
