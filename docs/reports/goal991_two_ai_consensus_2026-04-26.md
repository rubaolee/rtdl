# Goal991 Two-AI Consensus

Date: 2026-04-26

## Goal

Make the public prepared OptiX claim paths for ANN candidate coverage, facility service coverage, service coverage gaps, and event hotspot screening use scalar threshold-count continuation instead of count-row materialization.

## Codex Verdict

ACCEPT.

Codex implemented:

- `examples/rtdl_ann_candidate_app.py`: `candidate_threshold_prepared` now uses `prepared.count_threshold_reached(...)`.
- `examples/rtdl_facility_knn_assignment.py`: `coverage_threshold_prepared` now uses `prepared.count_threshold_reached(...)`.
- `examples/rtdl_service_coverage_gaps.py`: `gap_summary_prepared` now uses `prepared.count_threshold_reached(...)`.
- `examples/rtdl_event_hotspot_screening.py`: `count_summary_prepared` now uses `prepared.count_threshold_reached(...)` with `HOTSPOT_THRESHOLD + 1` to account for self-join counting.

Codex also updated public docs to state that these OptiX prepared modes are scalar count/decision paths, not witness-output paths.

Focused verification:

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

Additional checks:

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

git diff --check
```

Both checks passed.

## Gemini Verdict

ACCEPT.

Gemini review file:

- `docs/reports/goal991_gemini_review_2026-04-26.md`

Gemini confirmed that all four public OptiX prepared claim paths now avoid `prepared.run(...)`, use scalar `count_threshold_reached(...)`, keep witness/identity boundaries honest, and have adequate tests/docs. Gemini required no fixes.

## Consensus

Goal991 is closed with 2-AI consensus.

No public RTX speedup claim is authorized by this goal.
