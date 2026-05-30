# Handoff: Goal2690 Fresh Claude Re-Review

Please act as a fresh independent Claude reviewer, not as an author.

## Context

Goal2690 responds directly to:

- `docs/reviews/goal2689_claude_rereview_goal2688_hit_stream_contract_hardening_2026-05-29.md`

Goal2689 accepted Goal2688 with boundary but flagged F1/F2/F3/F5/F6 as fixes
needed before native CUDA hit-column implementation should begin.

## Files To Review

- `docs/reports/goal2690_post_goal2689_contract_honesty_fixes_2026-05-30.md`
- `docs/reports/goal2688_hit_stream_handoff_contract_hardening_after_claude_review_2026-05-29.md`
- `docs/reports/goal2685_device_resident_hit_stream_handoff_typed_payload_columns_2026-05-29.md`
- `docs/reviews/goal2689_claude_rereview_goal2688_hit_stream_contract_hardening_2026-05-29.md`
- `src/rtdsl/hit_stream_handoff.py`
- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `tests/goal2685_device_resident_hit_stream_handoff_test.py`
- `tests/goal2690_post_goal2689_contract_honesty_test.py`

Also keep in mind the broader v2.5 design reviews:

- `docs/reviews/v2_5_ten_benchmark_apps_baseline_readiness_review_2026-05-29.md`
- `docs/reviews/v2_5_goal_scoping_triton_runtime_and_tiered_benchmark_parity_2026-05-29.md`
- `docs/reports/v2_5_partner_choice_and_multi_partner_composition_design_2026-05-29.md`

## Review Questions

1. Does Goal2690 fully fix F1 so `caller_asserted` is not described as validated?
2. Does Goal2690 fully fix F2 so CUDA-shaped synthetic/native-column metadata cannot claim the host-materialization bottleneck was removed without hardware proof?
3. Does Goal2690 adequately resolve F3 ready/promoted wording in the RayDB v2.5 paths?
4. Does Goal2690 cover F5 `deferred_device_check` metadata at the contract-test level?
5. Is the RayDB CPU-reference float tolerance policy sufficient for future Triton sum/avg pod validation, or should it be stricter/different?
6. Are the remaining blockers now correctly limited to native ownership/lifetime, real OptiX CUDA columns, device-side validation, neutral buffer seam, and `sm_70+` pod evidence?
7. Is the code now safe to proceed to a non-pod design goal for the neutral buffer seam / ownership-lifetime state machine before hardware implementation?

## Expected Output

Write:

- `docs/reviews/goal2691_claude_review_goal2690_contract_honesty_fixes_2026-05-30.md`

Use one verdict:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

If you find problems, list file/line-level findings first, then recommendations.
