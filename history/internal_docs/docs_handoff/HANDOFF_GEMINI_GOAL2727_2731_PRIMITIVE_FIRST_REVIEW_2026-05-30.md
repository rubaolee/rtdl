# Handoff: Gemini Review For v2.5 Primitive-First Correction

Please perform an independent read-only review and write your review to:

`docs/reviews/goal2732_gemini_review_goal2727_2731_primitive_first_2026-05-30.md`

## Scope

Review the v2.5 primitive-first correction after the RayDB evidence and triangle-counting plan update.

Key files:

- `docs/reports/goal2727_raydb_prepared_grouped_reduction_opponent_2026-05-30.md`
- `docs/reports/goal2728_raydb_v2_5_primitive_first_planner_2026-05-30.md`
- `docs/reports/goal2730_triangle_counting_v2_5_primitive_first_plan_2026-05-30.md`
- `docs/reports/goal2731_raydb_minmaxavg_primitive_first_pod_evidence_2026-05-30.md`
- `docs/reviews/goal2729_claude_review_goal2726_2728_raydb_primitive_first_2026-05-30.md`
- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `tests/goal2728_raydb_v2_5_primitive_first_planner_test.py`
- `tests/goal2730_triangle_counting_v2_5_primitive_first_plan_test.py`
- `tests/goal2731_raydb_minmaxavg_primitive_first_pod_evidence_test.py`

## Questions

1. Is the primitive-first rule correct: use an existing fused app-agnostic RTDL primitive when it exactly matches the computation, and reserve typed hit-stream/partner continuation for unfused continuations?
2. Does the RayDB min/max/avg evidence close Claude's immediate measurement gap?
3. Does the triangle-counting plan avoid overclaiming and avoid relabeling native scalar summaries as Triton?
4. Are public speedup, true-zero-copy, and paper-reproduction claim boundaries preserved?
5. What remaining risks should be fixed before broader v2.5 benchmark migration?

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

State explicitly that this is an independent Gemini review distinct from Codex and Claude, and that Codex+Codex does not count as consensus.

