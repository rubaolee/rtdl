# Goal3062 v2.6 Native Tutorial and Example Pod Validation

Date: 2026-06-02

Status: native runtime validation for the curated v2.6 release-candidate
tutorial/example surface. This report validates runnable commands on a Linux
pod with Embree, OptiX/RT, and CuPy available; it does not authorize the v2.6
release button.

In short: this pod evidence does not authorize the v2.6 release button.

## Pod Surface

The user provided this pod access line:

```text
ssh root@213.173.105.24 -p 17444 -i ~/.ssh/id_ed25519
```

The current Codex environment used the established working key at
`~/.ssh/id_ed25519_rtdl_codex_current_pod`.

Validated environment:

| Item | Value |
| --- | --- |
| Repo path | `/root/rtdl` |
| Repo commit | `e126a1b93f138f527ad6d5cff256127dafbf6719` |
| GPU | `NVIDIA L4, 580.159.04` |
| OS | Ubuntu 24.04.3 |
| Python | Python 3.12.3 |
| CUDA runtime surface | `/usr/local/cuda`, `/usr/local/cuda-12`, `/usr/local/cuda-12.8` |
| CuPy | `14.1.1` |
| OptiX SDK | `v8.1.0` at `/root/vendor/optix-sdk` |
| OptiX library | `/root/rtdl/build/librtdl_optix.so` |
| Embree library | `/root/rtdl/build/librtdl_embree.so` |

Build steps completed on the pod:

```text
apt-get install -y libgeos-dev pkg-config libembree-dev cmake ninja-build
python3 -m pip install --upgrade pip
python3 -m pip install numpy pillow imageio imageio-ffmpeg cupy-cuda12x
git clone --depth 1 --branch v8.1.0 https://github.com/NVIDIA/OptiX_Apps.git /root/vendor/optix-sdk
make build-embree
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk
```

Runtime environment:

```text
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
export RTDL_EMBREE_LIBRARY=$PWD/build/librtdl_embree.so
```

## Result

The corrected curated pod runner passed every command:

```text
STEP_SUMMARY all_pass=True pass_count=21 total=21
```

Machine-readable evidence:

- `docs/reports/goal3062_v2_6_native_tutorial_example_pod_validation_2026-06-02.json`
- `docs/reports/goal3062_v2_6_native_tutorial_example_pod_validation_logs_2026-06-02/`

## Commands Validated

| # | Command name | Surface | Status |
| ---: | --- | --- | --- |
| 1 | `hello_world` | portable Python | pass |
| 2 | `hello_world_cpu_backend` | portable CPU backend | pass |
| 3 | `feature_quickstart_cookbook` | portable feature quickstart | pass |
| 4 | `hausdorff_cpu` | CPU reference | pass |
| 5 | `ann_cpu` | CPU reference | pass |
| 6 | `outlier_cpu` | CPU reference | pass |
| 7 | `dbscan_cpu` | CPU reference | pass |
| 8 | `robot_cpu` | CPU reference | pass |
| 9 | `barnes_cpu` | CPU reference | pass |
| 10 | `graph_cpu` | CPU reference | pass |
| 11 | `database_cpu` | CPU reference | pass |
| 12 | `road_hazard_cpu` | CPU reference | pass |
| 13 | `hausdorff_embree` | Embree native | pass |
| 14 | `hausdorff_optix_default` | OptiX native | pass |
| 15 | `hausdorff_optix_threshold_rtcore` | OptiX/RT threshold path | pass |
| 16 | `segment_polygon_anyhit_embree_counts` | Embree native | pass |
| 17 | `segment_polygon_anyhit_optix_counts` | OptiX native | pass |
| 18 | `polygon_pair_overlap_embree_summary` | Embree native | pass |
| 19 | `polygon_pair_overlap_optix_summary` | OptiX native | pass |
| 20 | `partner_anyhit_numpy_embree` | NumPy partner plus Embree | pass |
| 21 | `partner_anyhit_cupy_cuda_optix` | CuPy CUDA partner plus OptiX | pass |

## Documentation Fix Found During Validation

The first pod pass exposed one stale public-doc command spelling:

```text
--partner cupy --backend optix
```

The example parser accepts `numpy`, `torch-cuda`, and `cupy-cuda`, so the
release-facing docs were corrected to:

```text
--partner cupy-cuda --backend optix
```

The corrected command is covered by the final 21/21 pod runner as
`partner_anyhit_cupy_cuda_optix`.

## Boundaries

This validation authorizes only this statement:

The curated v2.6 release-candidate tutorial/example commands listed above run
on the configured Linux pod with Embree, OptiX/RT, and CuPy available.

This validation does not authorize:

- tagging or publishing v2.6;
- package-install claims;
- broad RT-core or whole-app speedup claims;
- automatic partner-selection claims;
- general zero-copy/device-residency claims;
- treating archived historical docs as current learner guidance.

## Remaining Release Gate

Goal3062 closes the native tutorial/example runtime gate that Goal3061 left
open. The final v2.6 release still requires the explicit user release decision
and final release consensus record.
