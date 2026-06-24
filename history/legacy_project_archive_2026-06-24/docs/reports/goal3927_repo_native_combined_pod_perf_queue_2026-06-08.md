# Goal3927 Repo-Native Combined Pod Performance Queue

Date: 2026-06-08

## Purpose

Goal3927 turns the Goal3923 markdown runbook into a checked-in Python runner:

`scripts/goal3927_combined_pod_perf_queue.py`

The next A5000 pod can run one repository command instead of pasting a long
remote shell script. This reduces SSH quoting risk and makes the queue easier to
test before pod execution.

## Queued Diagnostics

The runner executes the same two pending diagnostics:

- RayJoin LSI/overlay representative subprobe timing with shared loaded-case
  reuse.
- RTDBSCAN Numba grouped-stream column-signature timing for both unblocked and
  blocked query-range modes.

It writes all outputs under an artifact directory, then creates
`summary_manifest.json` with:

- source commit and dirty tracked-file status;
- RayJoin wrapper and nested subprobe timing fields;
- RTDBSCAN mode, partner, path label, blocked flag, block size, and signature
  strategy;
- all non-authorization claim-boundary flags.

## Dry Run

The runner supports a dry run that validates command shape without launching
expensive workloads:

```powershell
$env:PYTHONPATH='src;.'; py -3 scripts/goal3927_combined_pod_perf_queue.py --dry-run --output-dir scratch/goal3927_dry_run
```

## Pod Run Shape

On a fresh pod with data and `librtdl_optix.so` ready:

```bash
cd /root/rtdl
export PYTHONPATH=/root/rtdl_goal3788_clean_1780857956/.pydeps_goal3788_numba:src:.
export RTDL_OPTIX_LIBRARY=/root/rtdl_goal3788_clean_1780857956/build/librtdl_optix.so
python3 scripts/goal3927_combined_pod_perf_queue.py \
  --output-dir /root/goal3927_combined_perf_artifacts \
  --rayjoin-data-dir /root/rtdl/data/rayjoin_public_cdb \
  --step-timeout 900
```

The runner fails closed if the OptiX library or RayJoin CDB fixtures are
missing.

## Boundary

Goal3927 is orchestration only. It does not create performance evidence until
run on a real pod, does not install or repair OptiX, does not promote any route,
does not auto-select partners, and does not authorize public speedup, release,
true-zero-copy, RayJoin reproduction, or RTDBSCAN paper-reproduction wording.

## Validation

Run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3927_repo_native_combined_pod_perf_queue_test tests.goal3923_safe_next_pod_combined_perf_queue_test
```

Expected: all tests pass.
