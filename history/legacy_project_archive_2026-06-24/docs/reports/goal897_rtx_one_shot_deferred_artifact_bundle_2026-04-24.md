# Goal897 RTX One-Shot Deferred Artifact Bundle

Date: 2026-04-24

## Problem

The RTX pod one-shot runner could execute deferred benchmark entries with
`--include-deferred`, but its artifact bundle used mostly fixed glob patterns.
That covered active `goal759_*_rtx.json` outputs but risked omitting deferred
artifacts such as Goal887, Goal889, Goal873, and Goal877 outputs.

If the pod is expensive or temporarily available, missing artifacts from the
bundle would force manual recovery or a rerun.

## Change

`scripts/goal769_rtx_pod_one_shot.py` now reads the Goal759 manifest and adds
every existing manifest `--output-json` path to the tar bundle. When
`--include-deferred` is used, deferred-entry outputs are included as well.

The bundle metadata now records:

```text
include_deferred: true|false
member_count: <packaged artifact count>
```

## Verification

Command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal769_rtx_pod_one_shot_test
PYTHONPATH=src:. python3 -m py_compile scripts/goal769_rtx_pod_one_shot.py tests/goal769_rtx_pod_one_shot_test.py
git diff --check
```

Result:

```text
3 tests OK
py_compile OK
git diff --check OK
```

## Boundary

This is local cloud-run packaging work only. It does not execute cloud, does not
produce RTX performance evidence, and does not authorize any public speedup
claim.
