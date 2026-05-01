# Goal1207 Linux Embree Prefix Environment Fix

Date: 2026-05-01

Verdict: `LOCAL_FIX_READY_FOR_REVIEW`

## Problem

The Goal1204 RTX pod initially failed all Embree controls because Ubuntu `libembree-dev` provides Embree 3 while RTDL requires Embree 4. Installing Embree 4 under `/opt/embree-4.4.0` was not enough because the Linux Embree runtime ignored `RTDL_EMBREE_PREFIX` and defaulted to `/usr`.

The pod recovery succeeded only after creating `/usr/include/embree4` and `/usr/lib/libembree4.so` symlinks.

## Change

`src/rtdsl/embree_runtime.py` now honors `RTDL_EMBREE_PREFIX` before platform defaults on all operating systems, not only Windows.

This lets future Linux pods use:

```bash
export RTDL_EMBREE_PREFIX=/opt/embree-4.4.0
```

without mutating `/usr`.

## Validation

```bash
PYTHONPATH=src:. python3 -m unittest tests/goal1207_linux_embree_prefix_env_test.py
```

Result: `Ran 3 tests ... OK`

## Boundary

This is a local runtime environment fix. It does not change RTX benchmark results, public wording, or release status by itself.
