# Goal 952: Density Native Threshold Continuation

Date: 2026-04-25

## Scope

Goal952 hardens the outlier and DBSCAN app contracts so their compact density
paths explicitly report native backend threshold-count continuation.

This goal does not add a new speedup claim. It documents and tests the bounded
native continuation already used by the compact fixed-radius density paths:

- `outlier_detection`: prepared/compact fixed-radius threshold-count emits one
  density/outlier row per query without materializing neighbor rows.
- `dbscan_clustering`: prepared/compact fixed-radius threshold-count emits
  core flags without materializing neighbor rows.

## Code Changes

- `examples/rtdl_outlier_detection_app.py`
  - Added `native_continuation_active`.
  - Added `native_continuation_backend` with values:
    - `optix_threshold_count`
    - `embree_threshold_count`
    - `none`
  - Prepared OptiX sessions now expose the same native-continuation metadata.

- `examples/rtdl_dbscan_clustering_app.py`
  - Added the same native-continuation metadata.
  - Kept full DBSCAN cluster expansion explicitly Python-owned.
  - Prepared OptiX sessions now expose the same native-continuation metadata.

- `tests/goal952_density_native_continuation_test.py`
  - Verifies Embree compact outlier summaries report native continuation.
  - Verifies mocked prepared OptiX outlier summaries report native continuation.
  - Verifies Embree compact DBSCAN core flags report native continuation.
  - Verifies mocked prepared OptiX DBSCAN core flags report native continuation.
  - Verifies full CPU/Python DBSCAN clustering does not overstate native
    continuation.

## Documentation Updates

- `docs/application_catalog.md`
- `docs/app_engine_support_matrix.md`
- `examples/README.md`
- `src/rtdsl/app_support_matrix.py`

The docs now say the compact outlier and DBSCAN paths report native
threshold-count continuation while preserving these boundaries:

- No full DBSCAN cluster-expansion acceleration claim.
- No broad outlier-app speedup claim.
- No KNN, Hausdorff, ANN, Barnes-Hut, or general clustering claim from these
  fixed-radius density paths.
- No new public RTX speedup claim.

## Verification

Focused test gate:

```text
RTDL_FORCE_ORACLE_REBUILD=1 PYTHONPATH=src:. python3 -m unittest \
  tests.goal952_density_native_continuation_test \
  tests.goal741_embree_compact_app_perf_harness_test \
  tests.goal757_prepared_optix_fixed_radius_count_test \
  tests.goal690_optix_performance_classification_test \
  tests.goal803_rt_core_app_maturity_contract_test -v
```

Result:

```text
Ran 29 tests in 0.019s
OK (skipped=2)
```

The two skips are optional prepared OptiX native-library tests on this Mac.
Portable/mocked prepared OptiX tests passed.

Additional checks:

```text
PYTHONPATH=src:. python3 -m py_compile \
  examples/rtdl_outlier_detection_app.py \
  examples/rtdl_dbscan_clustering_app.py \
  src/rtdsl/app_support_matrix.py \
  tests/goal952_density_native_continuation_test.py
```

Result: pass.

```text
git diff --check -- \
  examples/rtdl_outlier_detection_app.py \
  examples/rtdl_dbscan_clustering_app.py \
  tests/goal952_density_native_continuation_test.py \
  docs/application_catalog.md \
  examples/README.md \
  docs/app_engine_support_matrix.md \
  src/rtdsl/app_support_matrix.py
```

Result: pass.

## Remaining Work

- Full DBSCAN connected-component expansion remains Python-owned.
- Density/outlier app speedup wording still requires same-semantics RTX review
  and should stay bounded to the prepared threshold-count sub-path.
- The next continuation targets should focus on remaining Python
  postprocess/refinement stages that can be moved behind native bounded
  summaries without overstating whole-app acceleration.
