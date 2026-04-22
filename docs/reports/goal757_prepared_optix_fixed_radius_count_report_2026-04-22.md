# Goal757 Prepared OptiX Fixed-Radius Count Report

## Verdict

ACCEPT.

Goal757 adds a prepared OptiX 2D fixed-radius count-threshold path for outlier detection and DBSCAN core-flag workloads. The implementation reuses the OptiX custom-primitive BVH across repeated query batches instead of rebuilding the search-point scene on every call.

## What Changed

- Native OptiX C ABI:
  - `rtdl_optix_prepare_fixed_radius_count_threshold_2d`
  - `rtdl_optix_run_prepared_fixed_radius_count_threshold_2d`
  - `rtdl_optix_destroy_prepared_fixed_radius_count_threshold_2d`
- Python runtime:
  - `rt.prepare_optix_fixed_radius_count_threshold_2d(search_points, max_radius=...)`
  - `PreparedOptixFixedRadiusCountThreshold2D.run(query_points, radius=..., threshold=...)`
- Apps:
  - `/Users/rl2025/rtdl_python_only/examples/rtdl_outlier_detection_app.py`
  - `/Users/rl2025/rtdl_python_only/examples/rtdl_dbscan_clustering_app.py`
- Performance harness:
  - `/Users/rl2025/rtdl_python_only/scripts/goal757_optix_fixed_radius_prepared_perf.py`
- Tests:
  - `/Users/rl2025/rtdl_python_only/tests/goal757_prepared_optix_fixed_radius_count_test.py`

## Design Note

The prepared handle takes `max_radius` because the OptiX custom-primitive AABBs must be wide enough for every later run-time query radius. The run call rejects `radius > max_radius` to prevent false negatives.

The traversal remains the same RT formulation already accepted for fixed-radius count-threshold:

- search points are represented as custom primitive AABBs padded by `max_radius`;
- query points launch orthogonal z-rays;
- the intersection program performs the exact 2D radius check;
- the any-hit program counts hits and calls `optixTerminateRay()` once the threshold is reached.

## Consensus

- Codex implementation verdict: accept.
- Gemini Flash plan review: `ACCEPT`, at `/Users/rl2025/rtdl_python_only/docs/reports/goal757_gemini_flash_plan_review_2026-04-22.md`.

## Correctness Evidence

macOS portable tests:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal757_prepared_optix_fixed_radius_count_test \
  tests.goal695_optix_fixed_radius_summary_test \
  tests.goal520_dbscan_clustering_app_test

Ran 18 tests in 0.425s
OK
```

macOS follow-up after native-test additions:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal757_prepared_optix_fixed_radius_count_test \
  tests.goal695_optix_fixed_radius_summary_test

Ran 13 tests in 0.002s
OK (skipped=2)
```

Linux native OptiX tests after rebuilding `build/librtdl_optix.so`:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so python3 -m unittest -v \
  tests.goal757_prepared_optix_fixed_radius_count_test \
  tests.goal695_optix_fixed_radius_summary_test \
  tests.goal520_dbscan_clustering_app_test

Ran 20 tests in 1.127s
OK
```

## Linux Scaled Performance

Artifact:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal757_optix_fixed_radius_prepared_perf_linux_gtx1070_2026-04-22.json`

Host: `lestat-lx1`, GTX 1070. This validates OptiX backend behavior and prepared-scene reuse only; it is not RTX RT-core speedup evidence.

Configuration:

- `copies=20000`
- `iterations=5`
- `point_count=160000`

| App | One-Shot Total (s) | Prepared OptiX Prepare (s) | Warm Query Median (s) | One-Shot / Warm Median |
|---|---:|---:|---:|---:|
| Outlier detection | 1.642629 | 0.229785 | 0.434524 | 3.78x |
| DBSCAN core flags | 1.102038 | 0.221430 | 0.434665 | 2.54x |

Both prepared outputs matched oracle-visible summaries.

## Boundary

- This goal accelerates the RT-heavy fixed-radius density predicate, not full DBSCAN cluster expansion.
- This goal does not change KNN, Hausdorff, ANN, or Barnes-Hut.
- This goal does not claim RTX RT-core speedup because the measured Linux GPU is GTX 1070.
- Default full-row app behavior remains available; the prepared modes are explicit performance surfaces.
