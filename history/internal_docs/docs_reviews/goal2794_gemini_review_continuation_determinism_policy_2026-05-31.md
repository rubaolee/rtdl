# Gemini Review - Goal2794 v2.5 Continuation Determinism Policy

Reviewer: Gemini (independent review)
Date: 2026-05-31
Reviewing: Goal2794 - v2.5 Continuation Determinism Policy

## Verdict

**accept**

This review finds that Goal2794 has successfully addressed the previously identified concerns regarding determinism, witness, and tie-breaking risks in v2.5 partner-continuation operations. The implementation establishes a clear and testable policy for these aspects, ensuring that determinism is explicitly defined and enforced across relevant operations.

## Findings

1.  **Policy Coverage:** The `V2_5_DETERMINISM_POLICIES` in `src/rtdsl/v2_5_determinism_policy.py` lists 12 policies, corresponding exactly to the operations defined in `V2_5_PARTNER_CONTINUATION_OPERATION_NAMES` from `src/rtdsl/partner_continuation_protocol.py`. The `validate_v2_5_continuation_determinism_policies` function and its corresponding test (`test_policy_covers_every_continuation_operation_once` in `tests/goal2794_v2_5_determinism_policy_test.py`) rigorously confirm that every v2.5 partner-continuation operation is covered exactly once.

2.  **Concreteness of Tie-Breaks and Tolerances:**
    *   For `grouped_argmin_f64`, `grouped_argmax_f64`, and `grouped_topk_f64`, the `tie_break_policy` explicitly includes "item_id" (e.g., "lowest_score_then_lowest_item_id") and `tolerance_policy` references "exact_score_or_documented_float_tolerance_for_backend". These are verified by `test_score_witness_operations_publish_item_id_tie_breaks`.
    *   For floating-point sums (`segmented_sum_f64`, `grouped_vector_sum_f64x2`), the `tolerance_policy` requires the backend to "publish reduction order or abs/rel tolerance", as checked by `test_float_reductions_publish_tolerance_or_order_policy`.
    *   For bounded collections (`bounded_collect_finalize_i64`) and event-ordered hit streams (`hit_stream_grouped_ray_id_primitive_i64`), the `overflow_policy` explicitly states "fail_closed_overflow" and "producer_overflow_fails_closed", respectively, which is verified by `test_bounded_and_event_stream_overflow_fail_closed`.
    These policies are sufficiently concrete for deterministic comparison.

3.  **App-Agnostic Implementation:** The `V25ContinuationDeterminismPolicy` dataclass, its validation logic (`__post_init__`, `validate_v2_5_continuation_determinism_policies`), and the associated test (`test_claim_flags_fail_closed_at_policy_and_row_level`) strictly enforce that flags like `public_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`, `release_readiness_authorized`, and `rt_traversal_replacement_allowed` are always `False`. This ensures the policy remains app-agnostic and avoids embedding app semantics into core runtime policy.

4.  **Avoidance of Overclaiming:** Consistent with app-agnosticism, the policy explicitly and programmatically prevents overclaiming. The `V2_5_DETERMINISM_POLICY_CLAIM_BOUNDARY` constant clearly defines this scope, and the code prevents any of the authorization flags (for speedup, release readiness, whole-app acceleration, or RT traversal replacement) from being set to `True` at both the top-level policy and individual operation levels. This is well-tested.

5.  **Test Sufficiency:** The `tests/goal2794_v2_5_determinism_policy_test.py` suite directly addresses the determinism and tie-break risks. It includes specific assertions for:
    *   Complete and unique operation coverage.
    *   Enforcement of claim boundaries.
    *   Specific tie-breaking rules for score-witness operations (`argmin`, `argmax`, `topk`).
    *   Tolerance and ordering requirements for floating-point reductions.
    *   Fail-closed behavior for bounded collection and hit-stream overflows.
    These tests provide a robust acceptance bar, directly operationalizing the design notes and preventing determinism/tie-break risks from becoming untracked.

## Explicit Statement

This is an independent Gemini review, distinct from Codex authoring.
