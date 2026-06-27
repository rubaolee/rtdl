# Gemini Review Task: Goal2340 Hausdorff v2.1 Benchmark Refresh

Please perform a read-only independent review of Goal2340 and write the result
to:

`docs/reviews/goal2341_gemini_review_goal2340_hausdorff_v2_1_refresh_2026-05-18.md`

## Context

RTDL v2.x must keep native engines app-agnostic. The Hausdorff/X-HD benchmark
is app-level Python using generic RTDL/OptiX point-group primitives:

- point-group threshold flags;
- nearest-witness rows;
- max-distance reduction;
- Python-level X-HD-style seeding/pruning.

Goal2340 refreshes the benchmark after the v2.1 RayJoin work. It does not add a
new native Hausdorff kernel and must not make a fresh performance claim until a
current-main pod rerun exists.

## Files To Inspect

- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/README.md`
- `scripts/goal2126_public_hausdorff_dataset_perf.py`
- `docs/reports/goal2340_hausdorff_v2_1_benchmark_refresh_2026-05-18.md`
- `tests/goal2340_hausdorff_v2_1_benchmark_refresh_test.py`
- Updated stale path tests:
  - `tests/goal2110_hausdorff_exact_rt_nearest_witness_test.py`
  - `tests/goal2112_hausdorff_v2_language_lab_test.py`
  - `tests/goal2121_xhd_point_group_hausdorff_optix_enhancement_test.py`
  - `tests/goal2123_xhd_point_group_nearest_reduction_test.py`
  - `tests/goal2131_xhd_seeded_pruned_hausdorff_test.py`

## Review Questions

1. Does the scale-aware `default_target_points_per_group()` default look
   technically reasonable for current X-HD-style point-set rows, while keeping
   explicit override knobs for reproducibility?
2. Does the change preserve the app-agnostic native-engine boundary?
3. Do the docs clearly present v2.1-compatible usage without claiming full
   X-HD reproduction, 3D surface Hausdorff, universal CUDA-vs-RT speedup, or a
   fresh current-main performance claim?
4. Are the stale test path repairs appropriate after the examples directory
   reorganization?
5. Is the pod rerun plan sufficient to produce a future current-main RTX
   performance artifact?

## Expected Verdict

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.

For this review, `accept-with-boundary` is expected if the local implementation
is sound but fresh pod timing remains pending.
