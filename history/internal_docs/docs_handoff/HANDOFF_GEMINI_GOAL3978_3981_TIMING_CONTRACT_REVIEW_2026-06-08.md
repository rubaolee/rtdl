# Handoff: Gemini Review For Goal3978-3981 Timing Contract Chain

Date: 2026-06-08

Please perform an independent read-only review of the Goal3978-3981 current
scale-profile timing contract chain.

## Commits

- `e077b28c` Goal3978 measure current scale repeatability
- `905d01e5` Goal3979 probe short row scale calibration
- `1f673c2f` Goal3980 add current scale hot path metric contract
- `b56d5fb3` Goal3981 backfill concrete current scale hot path metrics

## Files To Inspect

- `docs/reports/goal3978_current_scale_repeatability_probe_2026-06-08.md`
- `docs/reports/goal3978_current_scale_repeatability_probe_2026-06-08/aggregate.json`
- `tests/goal3978_current_scale_repeatability_probe_test.py`
- `docs/reports/goal3979_short_row_scale_calibration_probe_2026-06-08.md`
- `docs/reports/goal3979_short_row_scale_calibration_probe_2026-06-08/summary.json`
- `tests/goal3979_short_row_scale_calibration_probe_test.py`
- `src/rtdsl/current_benchmark_scale_profiles.py`
- `docs/reports/goal3980_current_scale_hot_path_metric_contract_2026-06-08.md`
- `tests/goal3980_current_scale_hot_path_metric_contract_test.py`
- `docs/reports/goal3981_current_scale_concrete_hot_path_metric_paths_2026-06-08.md`
- `tests/goal3981_current_scale_concrete_hot_path_metric_paths_test.py`
- context artifact:
  `docs/reports/goal3976_fresh_helper_current_scale_validation_2026-06-08/outputs/`

## Questions To Answer

1. Does Goal3978 correctly show repeatability for the current ten-app packet
   while identifying the short-row variance for robot collision and RayDB?
2. Does Goal3979 correctly reject blind repeat-count calibration for those rows
   and explain that wrapper/subprocess elapsed is not the hot-path metric?
3. Does Goal3980 correctly encode the wrapper-vs-hot-path boundary in the
   current scale-profile registry without changing app behavior or authorizing
   claims?
4. Does Goal3981 correctly replace the placeholder hot-path metric with concrete
   payload paths, including a composite RayJoin summary path?
5. Are the tests sufficient to guard the timing contract and keep release,
   public-speedup, broad RT-core, whole-app acceleration, true-zero-copy, AMD,
   paper-reproduction, package-install, auto-selection, and app-specific native
   logic claims blocked?
6. What should be the next benchmark-quality step before any claim-grade timing
   packet?

## Required Output

Use the verdict vocabulary `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

Write the review to:

`docs/reviews/goal3982_gemini_review_goal3978_3981_timing_contract_chain_2026-06-08.md`

Please keep this read-only except for writing the requested review file.
