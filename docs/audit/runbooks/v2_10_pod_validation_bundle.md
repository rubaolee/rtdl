# v2.10 Pod Validation Bundle

Status: current source-tree pod-validation runbook.

Use this runbook when a CUDA/OptiX pod is available and you want one bounded
entry point for the current v2.10 validation flow.

## Local Preflight

This is safe to run without a pod:

```bash
PYTHONPATH=src:. python scripts/rtdl_v2_10_pod_validation_bundle.py \
  --output-dir docs/reports/v2_10_pod_validation_bundle_preflight
```

It runs:

- the source-tree doctor;
- the benchmark evidence index;
- the ten-app front-door dry-run;
- the ten-app scale-profile dry-run.

## Hardware Run

On a configured NVIDIA pod with `RTDL_OPTIX_LIBRARY` set:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
python scripts/rtdl_v2_10_pod_validation_bundle.py \
  --run-front-door \
  --run-scale-profile \
  --output-dir docs/reports/v2_10_pod_validation_bundle_pod
```

To refresh CuPy-vs-Numba partner-continuation evidence in the same session:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
python scripts/rtdl_v2_10_pod_validation_bundle.py \
  --run-front-door \
  --run-scale-profile \
  --run-partner-comparison \
  --output-dir docs/reports/v2_10_pod_validation_bundle_pod
```

## Rules

- Do not use this bundle as package-install evidence.
- Do not publish speedup wording from a failed or partial bundle.
- Read `bundle_summary.json` first; every step must be `pass`.
- The bundle prints a start and completion line for each major step.
- The bundle does not move tags and does not authorize release claims.
