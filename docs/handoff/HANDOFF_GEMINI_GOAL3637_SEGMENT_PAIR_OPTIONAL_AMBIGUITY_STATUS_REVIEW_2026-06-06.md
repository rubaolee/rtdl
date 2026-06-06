# Handoff: Gemini Review for Goal3637 Optional Segment-Pair Ambiguity Status

Please perform an independent read-only review of Goal3637.

## Files to Inspect

- `docs/reports/goal3637_segment_pair_optional_ambiguity_status_2026-06-06.md`
- `docs/reports/goal3637_segment_pair_ambiguity_status_a5000/summary.json`
- `tests/goal3637_segment_pair_optional_ambiguity_status_test.py`
- `scripts/goal3631_segment_pair_backend_conformance_runner.py`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `docs/reports/goal3633_segment_pair_status_device_columns_2026-06-06.md`
- `docs/reports/goal3635_segment_pair_status_large_grid_stress_2026-06-06.md`

## Context

Goal3637 adds an optional strict-audit route for the app-agnostic
`segment_pair_left_id_dense_count` contract. The default hot route remains
Goal3633 count-plus-overflow. The new optional ABI symbol is:

`rtdl_optix_prepared_segment_pair_left_id_count_device_columns_with_ambiguity_status`

When requested, it launches a generic CUDA post-pass over resident left/right
segment arrays to count strict-v0 ambiguous pairs (`non_finite_input` or
`denominator_degenerate_or_collinear`) and returns an
`ambiguous_count_device_ptr`.

A5000 pod evidence at source commit `1eeff46c` shows:

- adversarial ambiguity count: 19/19;
- crossing grids 1024/2048/4096 ambiguity count: 0/0;
- `device_resident_column_count`: 3;
- `all_columns_device_resident`: true;
- `fallback_required`: false;
- all claim-boundary flags still false.

Focused local validation passed:

`py -3 -m unittest tests.goal3637_segment_pair_optional_ambiguity_status_test tests.goal3635_segment_pair_status_large_grid_stress_test tests.goal3633_segment_pair_status_device_columns_test tests.goal3631_segment_pair_backend_conformance_a5000_test tests.goal3625_segment_pair_intersection_contract_foundation_test tests.goal3627_segment_pair_typed_output_residency_contract_test tests.goal3629_segment_pair_dense_count_reference_oracle_test`

Result: 28 tests OK.

## Review Questions

1. Does the new optional route preserve the default hot route rather than forcing ambiguity scanning on every call?
2. Does the native/Python implementation remain app-agnostic and avoid RayJoin-specific logic?
3. Does the artifact support the claim that the optional route makes all three segment-pair status columns device-resident?
4. Is the report conservative enough about performance, first-use setup, true zero-copy, release, RT-core speedup, and RayJoin paper reproduction?
5. Are the ABI struct, ctypes struct, runtime metadata, runner, artifact, and test mutually consistent?

## Required Output

Write the review to:

`docs/reviews/goal3638_gemini_review_goal3637_segment_pair_optional_ambiguity_status_2026-06-06.md`

Use an explicit verdict such as `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.
