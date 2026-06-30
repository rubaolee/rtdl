# Goal2730: Triangle Counting v2.5 Primitive-First Plan

Date: 2026-05-30
Status: accepted as planning correction

## Purpose

Goal2728 established a v2.5 planner rule from RayDB: do not force typed hit streams or partner continuations when an existing fused app-agnostic RTDL primitive exactly matches the computation.

Goal2730 applies that rule to the RT-Graph triangle-counting benchmark plan. Triangle counting's primary benchmark result is a scalar summary, and the current code already has generic prepared RTDL summary primitives:

- `ray_triangle_weighted_any_hit_sum_3d` for RT-2A1;
- `ray_triangle_hit_count_sum_3d` for RT-1A2.

Therefore, the v2.5 plan should be primitive-first:

- select fused generic RTDL summaries for scalar triangle counts;
- reserve Triton segmented/compact-mask continuations for row streams, witness rows, or post-summary tensor work;
- avoid relabeling an existing native scalar summary as a Triton benchmark path.

## Files Updated

- `examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `tests/goal2725_triangle_counting_v2_5_plan_mode_test.py`
- `tests/goal2730_triangle_counting_v2_5_primitive_first_plan_test.py`

## Plan Metadata

`--mode v2_5_plan` now reports:

- `status = primitive_first_plan_recorded_native_summary_not_relabelled_as_triton`
- `selected_path = prepared_fused_generic_rt_summary`
- `alternative_path = row_stream_or_compact_mask_plus_triton_continuation`
- `typed_hit_stream_forced = false`
- `partner_continuation_required = false`
- `public_speedup_claim_authorized = false`
- `true_zero_copy_authorized = false`

The v2.5 migration manifest now records triangle counting as `primitive_first_rt_summary` instead of a forced partner-continuation row.

## Boundary

This goal does not add new performance evidence and does not change native code. It is a planning correction that prevents the v2.5 roadmap from using partner continuations where the fused generic RTDL primitive is already the right abstraction.

The next triangle-counting implementation work remains:

- build a single rerunnable large-data harness;
- compare the primitive-first scalar summary path against RT-Graph authors-code rows where available;
- add Triton continuation only for row-stream or compact-mask modes that genuinely need partner tensor work.

