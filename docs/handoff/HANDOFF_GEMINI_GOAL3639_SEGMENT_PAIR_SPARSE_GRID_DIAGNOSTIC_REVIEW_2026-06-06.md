# Handoff: Gemini Review for Goal3639 Segment-Pair Sparse-Grid Diagnostic

Please perform an independent read-only review of Goal3639.

## Files to Inspect

- `docs/reports/goal3639_segment_pair_sparse_grid_rt_index_diagnostic_2026-06-06.md`
- `docs/reports/goal3639_segment_pair_sparse_grid_a5000/summary.json`
- `docs/reports/goal3639_segment_pair_sparse_grid_a5000/large_summary.json`
- `tests/goal3639_segment_pair_sparse_grid_rt_index_diagnostic_test.py`
- `scripts/goal3631_segment_pair_backend_conformance_runner.py`
- `docs/reports/goal3635_segment_pair_status_large_grid_stress_2026-06-06.md`

## Context

Goal3635 showed that all-hit crossing grids are hostile to RT traversal and
that CuPy's dense arithmetic kernel is faster in that synthetic regime.
Goal3639 adds sparse diagonal segment-pair grids to the same app-agnostic
runner. These grids have `n*n` possible pairs but only `n` true hits.

A5000 evidence at source commit `89bae35b` shows same-contract correctness and
a sparse-regime crossover versus the runner's CuPy dense all-pairs baseline:

- 8192: CuPy kernel / OptiX wall = 1.306x
- 16384: CuPy kernel / OptiX wall = 2.395x
- 32768: CuPy kernel / OptiX wall = 5.135x

The report deliberately says this is a diagnostic only: not RayJoin
reproduction, not release evidence, not broad RT-core wording, not true
zero-copy, and not a public speedup claim.

Focused local validation passed:

`py -3 -m unittest tests.goal3639_segment_pair_sparse_grid_rt_index_diagnostic_test tests.goal3637_segment_pair_optional_ambiguity_status_test tests.goal3635_segment_pair_status_large_grid_stress_test tests.goal3633_segment_pair_status_device_columns_test tests.goal3631_segment_pair_backend_conformance_a5000_test tests.goal3625_segment_pair_intersection_contract_foundation_test tests.goal3627_segment_pair_typed_output_residency_contract_test tests.goal3629_segment_pair_dense_count_reference_oracle_test`

Result: 31 tests OK.

## Review Questions

1. Does the sparse-grid case correctly test the intended RT-index regime without app-specific/RayJoin logic?
2. Do the artifacts support the reported correctness and crossover ratios?
3. Is the interpretation conservative enough about synthetic data, baseline scope, public claims, and RayJoin reproduction?
4. Does Goal3639 accurately contrast with Goal3635's all-hit negative diagnostic?
5. Are report, artifacts, runner, and tests mutually consistent?

## Required Output

Write the review to:

`docs/reviews/goal3640_gemini_review_goal3639_segment_pair_sparse_grid_diagnostic_2026-06-06.md`

Use an explicit verdict such as `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.
