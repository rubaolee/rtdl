# Goal763 RTX Cloud Bootstrap Check

## Verdict

ACCEPT for local cloud-bootstrap tooling.

Goal763 adds a pre-benchmark bootstrap checker for the RTX cloud host. It is
designed to fail early on missing CUDA/OptiX/build prerequisites before paid
benchmark commands run.

## What Changed

- Added `/Users/rl2025/rtdl_python_only/scripts/goal763_rtx_cloud_bootstrap_check.py`.
- Added `/Users/rl2025/rtdl_python_only/tests/goal763_rtx_cloud_bootstrap_check_test.py`.
- Generated dry-run artifact:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal763_rtx_cloud_bootstrap_check_dry_run_2026-04-22.json`

## Cloud Sequence

Run this first on the RTX cloud host:

```bash
PYTHONPATH=src:. python3 scripts/goal763_rtx_cloud_bootstrap_check.py \
  --output-json docs/reports/goal763_rtx_cloud_bootstrap_check.json
```

If it succeeds, run the benchmark manifest:

```bash
PYTHONPATH=src:. python3 scripts/goal761_rtx_cloud_run_all.py \
  --output-json docs/reports/goal761_rtx_cloud_run_all_summary.json
```

Then summarize artifacts:

```bash
PYTHONPATH=src:. python3 scripts/goal762_rtx_cloud_artifact_report.py \
  --summary-json docs/reports/goal761_rtx_cloud_run_all_summary.json \
  --output-json docs/reports/goal762_rtx_cloud_artifact_report.json \
  --output-md docs/reports/goal762_rtx_cloud_artifact_report.md
```

## Checks Performed

The bootstrap checker records:

- `nvidia-smi` output;
- `nvcc --version`;
- detected `OPTIX_PREFIX`, `CUDA_PREFIX`, and `NVCC`;
- whether `optix.h`, `cuda.h`, and `nvcc` exist;
- git head and short status;
- `make build-optix`;
- focused native OptiX tests for prepared any-hit, prepared fixed-radius, and
  the robot phase profiler.

## Verification

```text
python3 -m py_compile \
  scripts/goal763_rtx_cloud_bootstrap_check.py \
  tests/goal763_rtx_cloud_bootstrap_check_test.py
```

Passed.

```text
PYTHONPATH=src:. python3 -m unittest -v tests.goal763_rtx_cloud_bootstrap_check_test

Ran 2 tests in 0.116s
OK
```

## Boundary

This is a readiness gate only. It does not run the app performance benchmarks
and does not authorize RTX speedup claims.
