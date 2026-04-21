# Goal 718: Embree Prepared App Modes

Date: 2026-04-21

## Verdict

ACCEPT for local implementation and focused validation.

Goal718 wires the Goal717 prepared Embree fixed-radius count-threshold runtime API into the public outlier and DBSCAN app surfaces.

## What Changed

- `examples/rtdl_outlier_detection_app.py`
  - Added `--embree-summary-mode rt_count_threshold_prepared`.
  - The prepared path uses `rt.prepare_embree_fixed_radius_count_threshold_2d(...)`.
  - It still emits one native summary row per query and does not materialize neighbor rows.
- `examples/rtdl_dbscan_clustering_app.py`
  - Added `--embree-summary-mode rt_core_flags_prepared`.
  - The prepared path uses `rt.prepare_embree_fixed_radius_count_threshold_2d(...)`.
  - It emits native core-flag summary rows only; full cluster expansion remains Python-side.
- Added focused app-mode tests:
  - `tests/goal718_embree_prepared_app_modes_test.py`
- Added app-batch perf harness:
  - `scripts/goal718_embree_prepared_app_batch_perf.py`

## Performance

Raw local perf JSON:

`/Users/rl2025/rtdl_python_only/docs/reports/goal718_embree_prepared_app_batch_perf_local_2026-04-21.json`

Environment:

- Host: `Rs-MacBook-Air.local`
- Embree: `4.4.0`
- Thread mode: `auto`, effective threads `10`

Prepared repeated app-summary speedup over one-shot app-summary:

| copies | points | outlier speedup | DBSCAN speedup |
|---:|---:|---:|---:|
| 512 | 4,096 | 1.53x | 1.69x |
| 2,048 | 16,384 | 1.66x | 1.58x |
| 8,192 | 65,536 | 1.37x | 1.39x |
| 32,768 | 262,144 | 1.36x | 1.40x |

Boundary:

- This measures repeated app summary phases with Python density/core conversion.
- It excludes full CLI JSON output and oracle comparison.
- Prepared mode reports run-only timing after one reusable Embree BVH prepare.
- A one-shot CLI invocation still cannot amortize preparation; prepared mode is primarily for repeated app/session workloads.

## Tests

Passed:

```text
PYTHONPATH=src:. python3 -m py_compile \
  examples/rtdl_outlier_detection_app.py \
  examples/rtdl_dbscan_clustering_app.py \
  scripts/goal718_embree_prepared_app_batch_perf.py \
  tests/goal718_embree_prepared_app_modes_test.py

PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal718_embree_prepared_app_modes_test \
  tests.goal717_embree_prepared_fixed_radius_summary_test \
  tests.goal715_embree_fixed_radius_summary_test
```

Result:

```text
Ran 7 tests in 0.016s
OK
```

## Status

The app surface now exposes the prepared Embree mode explicitly and the local batch harness shows repeated-query speedups. This is still a bounded local result. Linux and Windows large-scale multi-threaded perf are still required before making platform-level Embree performance claims.

## Review Status

- Codex implementation review: ACCEPT.
- Gemini 2.5 Flash Lite review: ACCEPT, saved at `/Users/rl2025/rtdl_python_only/docs/reports/goal718_gemini_flash_lite_review_2026-04-21.md`.
- Claude was not retried for Goal718 because the Goal717 call returned an account-limit message until 2pm America/New_York.

Consensus status: 2-AI consensus achieved by Codex plus Gemini Flash Lite.
