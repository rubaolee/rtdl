# Goal2994 - RayDB-Style v2.6 Numba Neutral Demonstrator Prepared

Date: 2026-06-01

## Purpose

Goal2994 moves v2.6 from generic Numba continuation conformance to the first benchmark-app demonstrator. The selected app is the RayDB-style grouped aggregate benchmark because its post-RT continuation naturally maps to the
currently supported Numba primitives:

- `segmented_count_i64`
- `segmented_sum_f64`

The demonstrator covers `avg_as_sum_count`, which uses both operations through
user-selected `partner="numba"`.

## What Changed

- `partner_group_count_by_key(..., partner="numba")` now routes through the
  v2.6 neutral partner handoff and then executes `run_numba_segmented_count_i64`.
- `partner_group_sum_by_key(..., partner="numba")` now routes through the
  v2.6 neutral partner handoff and then executes `run_numba_segmented_sum_f64`.
- The RayDB-style app exposes
  `describe_raydb_v2_6_numba_neutral_continuation(...)` and
  `run_raydb_v2_6_numba_neutral_continuation_preview(...)`.
- `scripts/goal2994_raydb_numba_neutral_demo_pod_runner.py` prepares a
  RayDB-style post-RT grouped aggregate fixture, copies app-lowered generic
  columns to Numba CUDA device arrays, runs the app-level Numba continuation,
  and validates CPU parity.

## Boundary

This is a post-RT continuation demonstrator, not a full RayDB paper reproduction. It does not replace RT traversal and does not claim RT-core speedup, whole-app speedup, public speedup, true zero-copy, Numba speedup, release readiness, automatic partner selection, or app-specific native engine logic.

`min` and `max` RayDB-style modes remain blocked for Numba until generic Numba
segmented min/max primitives exist.

## Pod Command

Use the same CUDA-12 `numba-cuda` site-activation pattern proven in Goal2993:

```bash
python3 /tmp/goal2994_runner_bootstrap.py
```

where the bootstrap adds the isolated `numba-cuda[cu12]` target as a site
directory before importing `numba.cuda`, then runs:

```bash
python3 scripts/goal2994_raydb_numba_neutral_demo_pod_runner.py --rows 1000000 --groups 4096 --block-size 256
```

Goal2994 is prepared; the L4 pod artifact will be recorded separately after
execution.
