# Goal2870 Consensus: Goal2868 Last-Day v2.5 Review Intake

Status: accepted for the internal v2.5 engineering lane.

Date: 2026-05-31

## Scope

This consensus covers the Goal2868 external review packet for the last-day v2.5
work from `3f8b1d5b` through `fbe28476`, plus the Goal2870 readiness-indexing
and compact runner fail-closed hardening response.

## Evidence

Call for review:

- `docs/handoff/CALL_FOR_REVIEW_GOAL2868_V2_5_LAST_DAY_WORK_SINCE_CLAUDE_REVIEWS_2026-05-31.md`

External reviews:

- `docs/reviews/goal2868_claude_review_v2_5_last_day_work_since_claude_reviews_2026-05-31.md`
- `docs/reviews/goal2868_gemini_review_v2_5_last_day_work_since_claude_reviews_2026-05-31.md`

Implementation response:

- `docs/reports/goal2870_v2_5_last_day_review_intake_and_runner_fail_closed_hardening_2026-05-31.md`

## Verdict

Codex implementation verdict: `accept-with-boundary`.

Claude independent review verdict: `accept-with-boundary`.

Gemini independent review verdict: `accept-with-boundary`.

Consensus verdict: `accept-with-boundary`.

The internal v2.5 packet is coherent and accepted for continued engineering
work, but final release remains blocked.

## Required Before Future Release Review

- Remove or fully route the legacy torch carrier through the neutral seam.
- Add per-op partner conformance tests across declared partners.
- Add kernel-level determinism/tie-break tests for witness, top-k, and floating
  reductions.
- Keep 7/7 canonical harness pass separate from Tier A/B parity claims.
- Treat Triton preview performance gaps as selection guidance until a preview
  wins same-contract timing.

## Boundary

This is Codex + Claude + Gemini internal engineering consensus. It is not v2.5 release consensus.
It does not authorize a release tag, public speedup wording,
broad RT-core speedup wording, whole-app speedup wording, true-zero-copy
wording, package-install wording, automatic Triton preview selection, or
app-specific native engine logic.
