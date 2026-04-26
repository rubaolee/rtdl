# Goal704 RunPod RTX A5000 Validation

Date: 2026-04-21

## Verdict

RTX-class validation path is now working on RunPod for the fixed-radius OptiX app profiler.

This is valid RTX hardware evidence for the exact tested environment:

- Provider: RunPod
- GPU: NVIDIA RTX A5000
- GPU memory: 24564 MiB
- Driver: 580.126.09
- CUDA runtime reported by driver: 13.0
- `nvcc`: CUDA 12.4, V12.4.131
- OptiX headers: `NVIDIA/optix-dev` tag `v9.0.0`
- RTDL commit: `09147a6`

## Local Artifact Copies

The RunPod-generated reports were copied back to:

- `/Users/rl2025/rtdl_python_only/docs/reports/runpod_2026-04-21/goal698_rtx_cloud_environment_2026-04-21.txt`
- `/Users/rl2025/rtdl_python_only/docs/reports/runpod_2026-04-21/goal698_rtx_cloud_fixed_radius_phase_profile_2026-04-21.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/runpod_2026-04-21/goal703_runpod_rtx_profile_report_2026-04-21.md`

## Setup Findings

The RunPod Pod did not include OptiX headers by default. Installing the versioned public OptiX headers fixed that:

```bash
mkdir -p "$HOME/vendor"
git clone --depth 1 --branch v9.0.0 https://github.com/NVIDIA/optix-dev.git "$HOME/vendor/optix-dev"
```

The first validation attempt then exposed two image dependencies:

- `gnu/stubs-32.h` was missing for CUDA/NVRTC/NVCC header resolution.
- `libgeos_c` was missing for RTDL's native oracle correctness path.

The following packages fixed the OS dependency gap on the tested Ubuntu image:

```bash
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y libc6-dev-i386 libgeos-dev pkg-config
```

CUDA 12.4 NVRTC rejected glibc math declarations in JIT mode for the older fixed-radius-neighbor runtime kernel path. RTDL's NVCC fallback works when explicitly configured:

```bash
export RTDL_OPTIX_PTX_COMPILER=nvcc
export RTDL_NVCC=/usr/local/cuda/bin/nvcc
```

The Goal698/Goal703 scripts were updated to set these variables for future cloud runs.

## Focused Correctness Result

After the environment fixes, the focused OptiX validation suite passed:

```text
Ran 22 tests in 1.367s
OK
```

Covered test modules:

- `tests.goal695_optix_fixed_radius_summary_test`
- `tests.goal696_optix_fixed_radius_linux_validation_test`
- `tests.goal697_optix_fixed_radius_phase_profiler_test`
- `tests.goal216_fixed_radius_neighbors_optix_test`
- `tests.goal690_optix_performance_classification_test`

## Performance Result

Run command:

```bash
python3 scripts/goal697_optix_fixed_radius_phase_profiler.py \
  --mode optix \
  --copies 128 \
  --iterations 5 \
  --output docs/reports/goal698_rtx_cloud_fixed_radius_phase_profile_2026-04-21.json
```

Generated summary report:

```bash
python3 scripts/goal699_rtx_profile_report.py \
  --profile-json docs/reports/goal698_rtx_cloud_fixed_radius_phase_profile_2026-04-21.json \
  --environment docs/reports/goal698_rtx_cloud_environment_2026-04-21.txt \
  --output docs/reports/goal703_runpod_rtx_profile_report_2026-04-21.md
```

Key medians from the generated report:

| app | row path total median (s) | summary path total median (s) | total ratio row/summary | row backend median (s) | summary backend median (s) | backend ratio row/summary |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| outlier_detection | 0.225426 | 0.174460 | 1.292 | 0.004152 | 0.003364 | 1.234 |
| dbscan_clustering | 0.183948 | 0.334450 | 0.550 | 0.003634 | 0.003466 | 1.049 |

Interpretation:

- Outlier fixed-radius summary is faster than the row path in total median and backend median.
- DBSCAN core-flag summary is slightly faster in backend median, but slower in total median because oracle/core-flag validation dominates this profiler path.
- The RTX A5000 result is review-eligible evidence, not an automatic broad speedup claim.

## Script Fixes Made After The Run

Updated:

- `/Users/rl2025/rtdl_python_only/scripts/goal698_rtx_cloud_validation_commands.sh`
- `/Users/rl2025/rtdl_python_only/scripts/goal703_runpod_rtx_validation_commands.sh`
- `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL703_RUNPOD_RTX_VALIDATION_HANDOFF_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/tests/goal698_rtx_cloud_validation_runbook_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal703_runpod_rtx_validation_handoff_test.py`

Fixes:

- Cloud validation exports `RTDL_NVCC` and defaults `RTDL_OPTIX_PTX_COMPILER=nvcc`.
- RunPod helper installs `libc6-dev-i386`, `libgeos-dev`, and `pkg-config` by default when run as root on an apt-based image.
- RunPod helper calls the report generator with the correct `--profile-json` and `--environment` arguments.
- Handoff now records the RTX A5000 setup details and package requirements.

Local verification of these script/doc changes:

```text
Ran 9 tests in 0.123s
OK
```

Additional checks:

- `bash -n scripts/goal703_runpod_rtx_validation_commands.sh scripts/goal698_rtx_cloud_validation_commands.sh`: OK
- `py_compile` for updated tests: OK
- `git diff --check`: OK

## Honesty Boundary

This result supports only these bounded statements:

- RTDL OptiX fixed-radius summary paths build and run correctly on a RunPod NVIDIA RTX A5000.
- The tested outlier summary path is faster than the row path at this benchmark size.
- The tested DBSCAN core-flag summary path reduces backend median slightly but does not improve total median under this oracle-heavy profiler.

Do not claim:

- broad RTDL OptiX speedup;
- KNN, Hausdorff, ANN, Barnes-Hut, graph, or DB RT-core speedup from this fixed-radius run;
- RTX 4090, L4, L40S, or Ada behavior from this RTX A5000 run;
- performance conclusions for untested apps.
