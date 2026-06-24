# Handoff - Gemini Review For Goal2792

Please write an independent Gemini review to:

`docs/reviews/goal2792_gemini_review_partner_selection_explain_plan_2026-05-31.md`

Review Goal2792, which adds an explain-only partner-selection helper on top of
Goal2791's thresholded guidance.

Files to inspect:

- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `src/rtdsl/__init__.py`
- `tests/goal2792_partner_selection_explain_plan_test.py`
- `tests/goal2791_thresholded_partner_selection_guidance_test.py`
- `docs/reports/goal2792_partner_selection_explain_plan_2026-05-31.md`
- `docs/reports/goal2791_thresholded_partner_selection_guidance_2026-05-31.md`

Questions to answer:

1. Does `explain_v2_5_partner_selection(...)` preserve the no-hidden-dispatch
   rule by returning `execution_strategy_selected: False`,
   `auto_select_partner_allowed: False`, and
   `requires_explicit_caller_choice: True`?
2. Is the 32K Hausdorff/X-HD result framed as an explicit Triton tiled candidate
   only, not an automatic performance path?
3. Does the helper keep negative and unknown guidance fail-closed?
4. Are public speedup, RT-core speedup, whole-app speedup, true-zero-copy, and
   release claims still blocked?

Use one of these verdicts exactly:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`
