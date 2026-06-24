# Gemini Review Request - Goal2775 Hit-Stream Neutral-Seam Reconciliation

Please perform an independent read-only review of Goal2775.

## Context

Goal2773's Claude review identified a concrete risk: `neutral_buffer_seam.py`
exists, but `hit_stream_handoff.py` still has Torch-carrier helper paths. The
design fix is not to remove Torch entirely. Torch remains a Triton launch
carrier in the current preview stack. The required fix is to make the neutral
buffer seam the authority and to prove Torch is not a hidden neutral protocol,
forced partner, silent cross-partner coercion, zero-copy proof, or speedup claim.

## Files To Inspect

- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/__init__.py`
- `tests/goal2775_hit_stream_neutral_seam_reconciliation_test.py`
- `docs/reports/goal2775_hit_stream_neutral_seam_reconciliation_2026-05-31.md`
- context:
  - `src/rtdsl/neutral_buffer_seam.py`
  - `src/rtdsl/v2_5_partner_support_matrix.py`
  - `tests/goal2692_neutral_buffer_seam_lifetime_contract_test.py`
  - `tests/goal2694_hit_stream_neutral_seam_metadata_test.py`
  - `tests/goal2698_hit_stream_partner_continuation_plan_test.py`
  - `tests/goal2740_hit_stream_cross_partner_transfer_plan_test.py`
  - `docs/reviews/goal2773_claude_review_v2_5_status_next_goals_2026-05-31.md`

## Required Checks

1. Confirm `describe_v2_5_hit_stream_neutral_seam_reconciliation()` makes the
   neutral buffer seam and support matrix the authority.
2. Confirm Torch is explicitly bounded to Triton carrier use only and is not
   treated as a neutral protocol or partner.
3. Confirm non-Triton partners (`cupy_conformance`, `numba`) use CUDA-array
   descriptor carriers, not Torch carrier protocols.
4. Confirm the new metadata does not authorize public speedup, true zero-copy,
   release readiness, or RT traversal replacement.
5. Confirm this is sufficient contract hardening before the next app-facing
   primitive/reduction goals.
6. List blockers or required follow-ups.

## Validation Commands

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2692_neutral_buffer_seam_lifetime_contract_test tests.goal2694_hit_stream_neutral_seam_metadata_test tests.goal2698_hit_stream_partner_continuation_plan_test tests.goal2740_hit_stream_cross_partner_transfer_plan_test tests.goal2774_v2_5_grouped_hit_stream_support_matrix_test tests.goal2775_hit_stream_neutral_seam_reconciliation_test
```

## Output

Write your review to:

`docs/reviews/goal2775_gemini_review_hit_stream_neutral_seam_reconciliation_2026-05-31.md`

Use verdict `accept`, `accept-with-boundary`, or `needs-more-evidence`.

Do not edit source code, tests, reports, or `MEMORY.md`.
