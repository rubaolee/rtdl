# Goal1624 v1.6.4 COLLECT_K_BOUNDED Stable-Promotion Decision 3-AI Consensus

Date: 2026-05-09

## Verdict

ACCEPTED as the v1.6.4 decision to defer stable `COLLECT_K_BOUNDED`
promotion and keep it experimental.

The evidence chain is accepted as reproducibility/test-sweep evidence only.
This consensus does not authorize public speedup wording, true zero-copy
wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, release
tags, or release action.

## Review Inputs

- Codex decision package:
  - `docs/reports/goal1624_v1_6_4_collect_k_stable_promotion_decision_2026-05-09.md`
  - `tests/goal1624_v1_6_4_collect_k_stable_promotion_decision_test.py`
- Evidence chain:
  - `docs/reports/goal1621_v1_6_4_collect_k_evidence_ledger_after_rtx_2026-05-09.md`
  - `docs/reports/goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_2026-05-09_report.md`
  - `docs/reports/goal1623_v1_6_4_rtx_a4500_collect_k_test_sweep_2026-05-09.md`
- Claude review:
  - `docs/reviews/goal1624_v1_6_4_collect_k_stable_promotion_decision_claude_review_2026-05-09.md`
- Gemini review:
  - `docs/reviews/goal1624_v1_6_4_collect_k_stable_promotion_decision_gemini_review_2026-05-09.md`

## Consensus Findings

Codex, Claude, and Gemini agree that the current v1.6.4 collect-k evidence
chain is useful and accepted for bounded reproducibility/test-sweep purposes,
but does not justify stable primitive promotion.

The accepted classification is:

`documented_experimental_candidate_with_representative_rtx_reproducibility_evidence`

Stable promotion is deferred because:

- the standing stable primitive target still excludes `COLLECT_K_BOUNDED`;
- implementation still includes diagnostic, gated-candidate, and
  environment-flagged optimization paths;
- RTX evidence is packet/sweep/reproducibility evidence, not public speedup
  evidence;
- reduced-copy evidence is not true zero-copy evidence.

## Claim Boundary

All reviewers agree this consensus is a deferral decision, not a promotion
decision. The following remain unauthorized:

- public speedup wording
- true zero-copy wording
- whole-app speedup claims
- broad RTX/GPU wording
- stable `COLLECT_K_BOUNDED` promotion
- release tags
- release action

Future stable promotion requires a new decision package and explicit 3-AI
consensus.
