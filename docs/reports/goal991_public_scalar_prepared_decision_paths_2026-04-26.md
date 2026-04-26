# Goal991 Public Scalar Prepared Decision Paths

Date: 2026-04-26

## Scope

Goal991 extends the Goal990 cleanup pattern to four public prepared OptiX decision/summary app paths that should avoid count-row materialization in their RT-core claim mode:

- `examples/rtdl_ann_candidate_app.py`
- `examples/rtdl_facility_knn_assignment.py`
- `examples/rtdl_service_coverage_gaps.py`
- `examples/rtdl_event_hotspot_screening.py`

## Changes

### ANN candidate coverage

`candidate_threshold_prepared` now uses:

```python
prepared.count_threshold_reached(case["query_points"], radius=radius, threshold=1)
```

instead of `prepared.run(...)`.

The OptiX prepared app path now emits scalar candidate-coverage decision fields:

- `covered_query_count`
- `within_candidate_radius`
- `summary_mode: scalar_threshold_count`
- `row_count: None`

Uncovered query IDs are not emitted when the scalar decision fails.

### Facility service coverage

`coverage_threshold_prepared` now uses:

```python
prepared.count_threshold_reached(case["customers"], radius=radius, threshold=1)
```

instead of `prepared.run(...)`.

The OptiX prepared app path now emits scalar service-coverage decision fields:

- `covered_customer_count`
- `all_customers_covered`
- `summary_mode: scalar_threshold_count`
- `row_count: None`

Uncovered customer IDs are not emitted when the scalar decision fails.

### Service coverage gaps

`gap_summary_prepared` now uses:

```python
prepared.count_threshold_reached(case["households"], radius=RADIUS, threshold=1)
```

instead of `prepared.run(...)`.

The OptiX prepared app path now emits scalar coverage counts and explicitly does not emit household IDs:

- `covered_household_count`
- `uncovered_household_ids: None`
- `coverage_summary_rows: ()`

Household IDs, clinic IDs, distances, and clinic-load counts remain row/Embree-summary responsibilities, not the OptiX scalar claim path.

### Event hotspot screening

`count_summary_prepared` now uses:

```python
prepared.count_threshold_reached(case["events"], radius=RADIUS, threshold=HOTSPOT_THRESHOLD + 1)
```

instead of `prepared.run(...)`.

The `+ 1` accounts for fixed-radius self-join semantics: the native count includes the query event itself, while the public hotspot threshold is defined over non-self neighbors.

The OptiX prepared app path now emits scalar hotspot count only:

- `hotspot_count`
- `hotspots: None`
- `neighbor_count_by_event: {}`
- `summary_rows: ()`

Hotspot event IDs and per-event neighbor counts remain row/Embree-summary responsibilities, not the OptiX scalar claim path.

## Honesty Boundaries

Goal991 narrows the public OptiX prepared claim paths to scalar decisions/counts.

- It does not claim nearest-neighbor ranking.
- It does not claim ANN indexing or quality-policy acceleration.
- It does not claim hotspot identity output on OptiX scalar mode.
- It does not claim uncovered household/customer/query witness output on OptiX scalar mode.
- It does not authorize any public speedup claim.

Rows and Embree summary modes remain available when witness identities are required.

## Tests

Focused local gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal810_spatial_apps_optix_summary_surface_test \
  tests.goal819_spatial_prepared_summary_rt_core_gate_test \
  tests.goal880_ann_candidate_threshold_rt_core_subpath_test \
  tests.goal881_facility_coverage_optix_subpath_test \
  tests.goal955_spatial_prepared_native_continuation_test \
  tests.goal811_spatial_optix_summary_phase_profiler_test \
  tests.goal887_prepared_decision_phase_profiler_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal821_public_docs_require_rt_core_test

Ran 46 tests in 0.758s
OK
```

Compile check:

```text
python3 -m py_compile \
  examples/rtdl_ann_candidate_app.py \
  examples/rtdl_facility_knn_assignment.py \
  examples/rtdl_service_coverage_gaps.py \
  examples/rtdl_event_hotspot_screening.py \
  tests/goal810_spatial_apps_optix_summary_surface_test.py \
  tests/goal880_ann_candidate_threshold_rt_core_subpath_test.py \
  tests/goal881_facility_coverage_optix_subpath_test.py \
  tests/goal955_spatial_prepared_native_continuation_test.py
```

Result: OK.

`git diff --check`: OK.

## Docs Updated

- `docs/app_engine_support_matrix.md`
- `docs/application_catalog.md`
- `docs/v1_0_rtx_app_status.md`

## Status

Codex verdict: ACCEPT, pending second-AI review and consensus closure.
