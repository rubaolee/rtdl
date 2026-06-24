# Recorded External Review: Phoenix V3 M38 Component-Union Focused POD Protocol

Date: 2026-06-23

Reviewer: Claude

Raw review:

- `docs/reviews/claude_phoenix_v3_m38_component_union_focused_pod_protocol_compact_retry_review_2026-06-23.raw.md`

## Verdict

`accept_m38_authorize_one_focused_component_union_pod_after_harness_gate`

## Recorded Interpretation

Claude accepts M38 as a focused component-union POD protocol packet. The review
does not authorize an immediate POD run. It authorizes exactly one later focused
POD only after the M39 harness exists, passes local dry-run/unit gates, enforces
same generated input across variants, confirms RT hardware, prints heartbeat
output, and preserves the hard cap.

## Reasons Accepted

- The row is serious enough for a focused Set-A component-union probe:
  clustered 3D fixed-radius component-union labels at `262144` points,
  warmup `1`, repeat `5`.
- The variants are same-contract because all three must produce component-label
  outputs and canonical component signatures.
- The protocol blocks component-signature shortcuts through pre-run gates,
  failure classification, required runner metadata, and correctness wording.
- The success bars require `1.20x` over Embree on both hot query median and
  runner-inclusive wall, plus `0.98x` no-regression against legacy OptiX.
- The resource cap is bounded at `2h / $0.50` before new review.

## Required Follow-Ups Before Any POD Spend

1. Implement `scripts/v3_phoenix_component_union_m38_pod_ab.py` or an
   equivalent reviewed runner harness in M39.
2. The harness must use the same generated point set for all three variants.
3. The harness must confirm the OptiX RT hardware gate on the target machine.
4. The harness must print heartbeat output at least every 30 seconds.
5. The harness or caller must enforce the `2h / $0.50` hard cap.

## Non-Authorization

This recorded review authorizes no V3 release, no all-app POD spend, no public
speedup wording, no broad V3-over-V2 wording, no true-zero-copy wording, no
automatic partner selection, no V4 work, no C ABI work, and no embedding work.

## Goal-Level Decision Audit

Decision: accept Claude's M38 verdict as external review input while preserving
the harness gate and non-authorization boundaries.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   It would be foolish to read the verdict as immediate POD permission or
   release evidence. The verdict is conditional on M39 harness gates.

3. Was there another path?

   Yes. Keep waiting for Gemini or Antigravity despite hard tool failures. That
   would stall useful V3 work without adding review quality.

4. Can I now try a different path that actually solves the problem?

   Yes. Record the review, form Codex+Claude consensus, and move next to M39
   local harness implementation before any paid run.
