# Handoff: Claude Review For Goal2726-Goal2728 RayDB Primitive-First Correction

Please perform an independent read-only review of the recent v2.5 RayDB work and write your review to:

`docs/reviews/goal2729_claude_review_goal2726_2728_raydb_primitive_first_2026-05-30.md`

## Context

Recent pushed commits:

- `1fa2fc23` - Goal2726 diagnostic comparison of old `paper_rt_optix` vs v2.5 prepared hit stream.
- `861ae819` - Goal2727 implementation of `paper_rt_optix_prepared_grouped_reduction`.
- `0363a888` - Goal2727 large pod evidence showing prepared fused grouped reduction beats prepared hit-stream+Triton for RayDB count/sum.
- `efae208f` - Goal2728 primitive-first planner backend `paper_rt_optix_v2_5_primitive_first`.
- `782dcc17` - runner metadata exposes primitive-first planner decisions.
- `6de30b9c` - Goal2728 pod artifact/report/test.

## Files To Inspect

- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `scripts/goal2685_raydb_device_hit_stream_handoff_pod_runner.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `docs/reports/goal2726_raydb_v24_native_vs_v25_prepared_probe_2026-05-30.md`
- `docs/reports/goal2727_raydb_prepared_grouped_reduction_opponent_2026-05-30.md`
- `docs/reports/goal2728_raydb_v2_5_primitive_first_planner_2026-05-30.md`
- `tests/goal2726_raydb_v24_native_vs_v25_prepared_probe_test.py`
- `tests/goal2727_raydb_prepared_grouped_reduction_opponent_test.py`
- `tests/goal2728_raydb_v2_5_primitive_first_planner_test.py`

## Review Questions

1. Is the Goal2727 negative result interpreted correctly: typed hit-stream+Triton should not replace an existing faster fused generic RTDL primitive for RayDB grouped count/sum?
2. Does `paper_rt_optix_v2_5_primitive_first` keep the native engine app-agnostic while recording an explicit selected backend/path/fallback reason?
3. Are the claim boundaries correct: no public speedup, no true zero-copy, no RayDB reproduction claim?
4. Is the v2.5 manifest update honest, or does it overcorrect by weakening the partner-continuation roadmap?
5. What exact next risks should be fixed before broader v2.5 benchmark migration continues?

## Expected Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

The review must be independent, must state that Claude is distinct from Codex, and must not count Codex+Codex as consensus.

