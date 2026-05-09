# Goal1609 v1.6.x Performance Roadmap 3-AI Consensus

Date: 2026-05-09

## Scope

Review of the roadmap for using `v1.6.1` through `v1.6.10` as the
Python+RTDL performance-boosting lane after the published `v1.6` architecture
milestone.

Roadmap file:

- `docs/reports/goal1609_v1_6_x_performance_roadmap_2026-05-09.md`

## Codex Verdict

ACCEPT.

Codex accepts the roadmap because it puts measurement before optimization,
keeps pod usage batched and evidence-driven, treats `COLLECT_K_BOUNDED` as
experimental until a fail-closed promotion gate passes, preserves the
reduced-copy versus true-zero-copy distinction, and requires exact same-contract
evidence before public speedup wording.

## Claude Verdict

ACCEPT.

Claude found the roadmap clear, safely sequenced, claim-safe, and practical.
Claude noted four non-blocking improvements:

- re-sample `COLLECT_K_BOUNDED` OptiX performance after later optimization work;
- ensure v1.6.6 session paths are included in the v1.6.8 measurement package;
- define "positive control";
- clarify the relationship between thin result views and session APIs.

These notes were incorporated into the roadmap.

Review file:

- `docs/reviews/goal1609_v1_6_x_performance_roadmap_claude_review_2026-05-09.md`

## Gemini Verdict

ACCEPT.

Gemini found the roadmap clear, safely sequenced, claim-safe, and practical.
Gemini specifically accepted measurement-before-optimization, the reduced-copy
versus true-zero-copy boundary, careful OptiX/NVIDIA pod policy, and the
v1.6.9 public-claim audit gate.

Review file:

- `docs/reviews/goal1609_v1_6_x_performance_roadmap_gemini_review_2026-05-09.md`

## Consensus

The v1.6.x performance roadmap is accepted by Codex, Claude, and Gemini.

The next concrete goal should be Goal1610: create the v1.6.x phase/copy
measurement manifest and local runner skeleton. Do not start paid NVIDIA pod
work until local measurement commands, artifact paths, parity checks, and
positive controls are ready.

## Non-Authorization

This consensus does not authorize:

- a new release tag;
- moving or retagging `v1.6`;
- public speedup wording;
- whole-app speedup wording;
- true zero-copy wording;
- package-install wording;
- partner tensor handoff claims;
- stable `COLLECT_K_BOUNDED` promotion.
