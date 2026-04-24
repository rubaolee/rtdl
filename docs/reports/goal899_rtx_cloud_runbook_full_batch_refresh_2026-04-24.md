# Goal899 RTX Cloud Runbook Full-Batch Refresh

Date: 2026-04-24

## Result

The RTX cloud single-session runbook now recommends one full active+deferred
pod command for the current v0.9.8/v1.0 app-prep packet.

## What Changed

The runbook now:

- uses `--include-deferred` in the primary pod command
- explains that active entries and deferred readiness gates run in the same pod
  session
- keeps `--only` only for targeted retry if one deferred gate fails
- documents that the artifact bundle includes manifest `--output-json` outputs,
  including deferred outputs when `--include-deferred` is used

## Why

Cloud availability is unstable and paid pod sessions should not be restarted per
app. The current local policy is to prepare everything locally, then run one
maximal pod session when cloud is available.

## Verification

Command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal769_rtx_pod_one_shot_test

PYTHONPATH=src:. python3 -m py_compile \
  tests/goal829_rtx_cloud_single_session_runbook_test.py \
  scripts/goal769_rtx_pod_one_shot.py

git diff --check
```

Result:

```text
7 tests OK
py_compile OK
git diff --check OK
```

## Boundary

This is documentation and local dry-run/runbook preparation only. It does not
start cloud and does not authorize performance or speedup claims.
