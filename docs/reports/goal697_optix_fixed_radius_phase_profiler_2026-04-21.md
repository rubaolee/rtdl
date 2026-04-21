# Goal697 OptiX Fixed-Radius Phase Profiler

Date: 2026-04-21

Verdict: ACCEPT as an RTX-ready measurement harness. This goal does not claim
an RTX speedup.

## Scope

Goal697 adds:

- `/Users/rl2025/rtdl_python_only/scripts/goal697_optix_fixed_radius_phase_profiler.py`
- `/Users/rl2025/rtdl_python_only/tests/goal697_optix_fixed_radius_phase_profiler_test.py`

The profiler covers the two fixed-radius app paths introduced around
Goal695/Goal696:

- outlier detection, default emitted neighbor-row path;
- outlier detection, OptiX fixed-radius count-threshold summary path;
- DBSCAN, default emitted neighbor-row path;
- DBSCAN, OptiX fixed-radius core-flag summary path.

## Measured Phases

The script records app-level phase splits:

- `python_input_construction`
- `backend_execute_or_materialize_rows`
- `python_postprocess`
- `oracle_validate`
- `oracle_core_flag_validate` for DBSCAN core flags
- `total`

The output is JSON and includes:

- `classification_change: false`
- `rtx_speedup_claim: false`
- `hardware_boundary`
- `native_subphase_boundary`
- one case record per app/path pair

## Native Boundary

The current native fixed-radius ABI returns whole-call results only. Packing,
BVH build, OptiX launch, and copy-back are not separately timed until the native
API exposes counters or phase-return metadata.

Therefore this is an RTX-ready phase profiler, not a full native kernel
micro-profiler.

## Honesty Boundary

No RTX speedup claim is made by this report.

GTX 1070 timing is not RT-core timing. A valid RT-core performance claim
requires running the script in `--mode optix` on RTX-class hardware such as
NVIDIA L4/A10/Ada/Ampere/Lovelace and recording the full environment.

Outlier detection and DBSCAN app classifications do not change in this goal.
The summary paths reduce row materialization, but the project still needs
RTX-class measurements before promoting them beyond the existing conservative
classification.

## Usage

Dry-run mode, safe on any developer machine:

```bash
PYTHONPATH=src:. python3 scripts/goal697_optix_fixed_radius_phase_profiler.py \
  --mode dry-run \
  --copies 1 \
  --iterations 3
```

OptiX mode, for Linux with a built RTDL OptiX library:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIB=/path/to/librtdl_optix.so \
python3 scripts/goal697_optix_fixed_radius_phase_profiler.py \
  --mode optix \
  --copies 128 \
  --iterations 5 \
  --output docs/reports/goal697_optix_fixed_radius_phase_profile_linux_rtx_YYYY-MM-DD.json
```

## Local Verification

Required local checks:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal697_optix_fixed_radius_phase_profiler_test \
  tests.goal696_optix_fixed_radius_linux_validation_test \
  tests.goal690_optix_performance_classification_test

PYTHONPATH=src:. python3 -m py_compile \
  scripts/goal697_optix_fixed_radius_phase_profiler.py \
  tests/goal697_optix_fixed_radius_phase_profiler_test.py

git diff --check
```

## Release Meaning

This goal prepares the next cloud/RTX validation step. Once an AWS/GCP/Azure
NVIDIA L4/A10/RTX machine is available, this same script should be run without
changing app semantics. The expected release evidence should compare default
row paths against summary paths while preserving oracle parity and clearly
separating app-level timing from native subphase timing.
