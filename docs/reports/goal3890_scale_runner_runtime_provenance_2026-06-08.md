# Goal3890 Scale Runner Runtime Provenance

## Purpose

Goal3888 showed that the current scale-profile runner artifact was missing
self-contained source and hardware provenance. The report had to record the pod
commit and GPU manually.

Goal3890 adds generic runtime provenance to
`scripts/goal3828_current_benchmark_scale_profile_runner.py` so future dry-run
and pod artifacts carry that context inside `summary.json`.

## What Changed

The runner now emits top-level `runtime_environment` metadata:

- `source_commit`
- `source_commit_short`
- `git_status_short`
- `working_tree_clean`
- `python_executable`
- `python_version`
- `cwd`
- RTDL library environment variables:
  - `RTDL_OPTIX_LIBRARY`
  - `RTDL_OPTIX_LIB`
  - `RTDL_EMBREE_LIBRARY`
  - `RTDL_HIPRT_LIBRARY`
  - `CUDA_VISIBLE_DEVICES`
- optional `nvidia_smi` text from
  `nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader`

The metadata command helper is best-effort and bounded by a 10-second timeout.
If Git or `nvidia-smi` is unavailable, the field is recorded as `null` rather
than failing the benchmark run.

## Boundary

Goal3890 is provenance only. It does not change any benchmark row command,
timeout, stdout parsing, prepared-session profile attachment, or claim-boundary
scanner.

It does not authorize release action, public speedup wording, broad RT-core
wording, true-zero-copy wording, automatic partner/backend selection, AMD
performance wording, or app-specific native-engine logic.

## Validation

Added `tests/goal3890_scale_runner_runtime_provenance_test.py`.

The test runs the runner in dry-run mode and checks that the artifact includes
source commit fields, git-status fields, Python runtime fields, RTDL library
environment fields, and optional `nvidia_smi`, while leaving all claim
authorization flags false.
