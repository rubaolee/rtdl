# Goal992 Outlier/DBSCAN Scalar Public Paths

Date: 2026-04-26

## Scope

Goal992 adds explicit scalar public output modes for the two fixed-radius density apps whose existing prepared modes still legitimately support per-point labels:

- `examples/rtdl_outlier_detection_app.py`
- `examples/rtdl_dbscan_clustering_app.py`

This goal does not remove the existing per-point modes. It adds separate scalar modes for the RT-core claim path.

## Changes

### Outlier Detection

New scalar mode:

```text
--backend optix --optix-summary-mode rt_count_threshold_prepared --output-mode density_count
```

The mode calls:

```python
prepared.count_threshold_reached(points, radius=RADIUS, threshold=MIN_NEIGHBORS_INCLUDING_SELF)
```

and returns:

- `threshold_reached_count`
- `outlier_count`
- `oracle_outlier_count`
- `density_rows: ()`
- `outlier_point_ids: None`
- `summary_mode: scalar_threshold_count`

Existing `density_summary` remains available when per-point outlier labels are required.

The prepared session also accepts `output_mode="density_count"` and uses the same scalar call.

### DBSCAN

New scalar mode:

```text
--backend optix --optix-summary-mode rt_core_flags_prepared --output-mode core_count
```

The mode calls:

```python
prepared.count_threshold_reached(points, radius=EPSILON, threshold=MIN_POINTS)
```

and returns:

- `threshold_reached_count`
- `core_count`
- `oracle_core_count`
- `core_flag_rows: ()`
- `summary_mode: scalar_threshold_count`

Existing `core_flags` remains available when per-point core labels are required. Full DBSCAN cluster expansion remains Python-side and outside the RT-core claim.

The prepared session also accepts `output_mode="core_count"` and uses the same scalar call.

## Honesty Boundaries

- `density_count` does not emit outlier point IDs.
- `core_count` does not emit per-point core flags.
- Neither mode claims full anomaly detection, full DBSCAN clustering, connected components, KNN, Hausdorff, ANN, or Barnes-Hut behavior.
- This goal does not authorize any public RTX speedup claim.

## Tests

Focused local gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal757_prepared_optix_fixed_radius_count_test \
  tests.goal695_optix_fixed_radius_summary_test \
  tests.goal741_embree_compact_app_perf_harness_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal821_public_docs_require_rt_core_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal700_fixed_radius_summary_public_doc_test \
  tests.goal952_density_native_continuation_test

Ran 45 tests in 0.019s
OK (skipped=2)
```

Additional checks:

```text
python3 -m py_compile \
  examples/rtdl_outlier_detection_app.py \
  examples/rtdl_dbscan_clustering_app.py \
  tests/goal757_prepared_optix_fixed_radius_count_test.py

git diff --check
```

Both checks passed.

## Docs Updated

- `docs/app_engine_support_matrix.md`
- `docs/application_catalog.md`
- `docs/v1_0_rtx_app_status.md`
- `docs/release_facing_examples.md`
- `README.md`
- `examples/README.md`

Follow-up front-page doc check:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal700_fixed_radius_summary_public_doc_test \
  tests.goal821_public_docs_require_rt_core_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal958_public_app_native_continuation_schema_test

Ran 16 tests in 0.134s
OK
```

## Status

Codex verdict: ACCEPT, pending second-AI review and consensus closure.
