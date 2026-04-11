# Goal 246: Verification Surface Audit Pass

## Objective

Record the first seeded tier-6 pass for the release-critical verification
surface.

## Scope

This pass covers the tests that most directly anchor the released
nearest-neighbor and harness claims:

- `tests/goal200_fixed_radius_neighbors_embree_test.py`
- `tests/goal201_fixed_radius_neighbors_external_baselines_test.py`
- `tests/goal207_knn_rows_external_baselines_test.py`
- `tests/goal216_fixed_radius_neighbors_optix_test.py`
- `tests/goal217_knn_rows_optix_test.py`
- `tests/goal218_fixed_radius_neighbors_vulkan_test.py`
- `tests/goal219_knn_rows_vulkan_test.py`
- `tests/goal223_vulkan_harness_integration_test.py`
- `tests/goal228_v0_4_nearest_neighbor_perf_harness_test.py`
- `tests/report_smoke_test.py`

## Required Checks

- the verification slice still passes as a bounded suite
- skipped GPU tests remain explicit and honest rather than silently omitted
- external baseline and harness tests still match the released v0.4.0 surface
- smoke-level report generation paths remain intact
