# Handoff: Goal2688 Fresh Claude Re-Review

Please act as a fresh independent Claude reviewer, not as an author.

## Work To Review

Goal2688 responds to the previous fresh Claude critique in:

- `docs/reviews/goal2687_claude_fresh_critical_v2_5_design_roadmap_perf_risk_review_2026-05-29.md`

Read these updated files:

- `docs/reports/goal2688_hit_stream_handoff_contract_hardening_after_claude_review_2026-05-29.md`
- `docs/reports/goal2685_device_resident_hit_stream_handoff_typed_payload_columns_2026-05-29.md`
- `docs/rtdl_primitive_catalog.md`
- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/__init__.py`
- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `tests/goal2685_device_resident_hit_stream_handoff_test.py`

## Review Questions

1. Did Goal2688 correctly stop overclaiming that Goal2685 delivers device-resident handoff?
2. Are the new metadata fields sufficient to make host materialization, removed-bottleneck status, zero-copy status, and API maturity machine-checkable?
3. Is removing the experimental names from `rtdsl.__all__` enough to avoid implying stable public API promotion while preserving internal/direct use?
4. Is the new `group_id_bounds_validation` contract acceptable as an interim design, or is it still too risky without a device-side error-flag kernel?
5. Does the new primitive-id bounds check fail closed clearly enough?
6. Do the updated tests cover the important missing paths from Goal2687, including native-device-column constructor metadata, overflow, primitive-id range errors, count/sum/min/max reference continuation, and optional Torch/CUDA gather?
7. Does any wording in the updated reports/catalog/example still imply true zero-copy, removed host bottleneck, broad RT-core speedup, or release readiness?
8. What exact blockers remain before a real native OptiX CUDA-resident hit-column implementation should begin?

## Expected Output

Write:

- `docs/reviews/goal2689_claude_rereview_goal2688_hit_stream_contract_hardening_2026-05-29.md`

Use verdicts from:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

If you find problems, list file/line-level findings first, then recommendations.
