# Goal1208 Two-AI Consensus

Date: 2026-05-01

Verdict: `ACCEPT`

## Scope

Goal1208 is a public wording decision packet after accepted Goal1206 RTX 4090 evidence. It does not edit public docs or authorize release by itself.

## Evidence

- Decision packet: `docs/reports/goal1208_public_wording_decision_after_goal1206_2026-05-01.md`
- Decision JSON: `docs/reports/goal1208_public_wording_decision_after_goal1206_2026-05-01.json`
- Source consensus: `docs/reports/goal1206_two_ai_consensus_2026-05-01.md`
- Gemini attempt blocked: `docs/reports/goal1208_gemini_public_wording_decision_review_attempt_blocked_2026-05-01.md`
- Claude review: `docs/reports/goal1208_claude_public_wording_decision_review_2026-05-01.md`

## Decisions Accepted

- `road_hazard_screening`: proposed bounded reviewed wording.
  - Evidence: 40k same-scale, OptiX `0.230652s`, Embree `0.814722s`, ratio `3.53x`.
- `database_analytics`: repaired but positive public speedup wording remains blocked.
  - Evidence: 100k/300k ratios `1.12x` and `1.16x`, below the `1.2x` public threshold.
- `polygon_set_jaccard`: correctness-ready but speedup wording blocked.
  - Evidence: public-safe chunk 512 parity passed; chunk 64 remains diagnostic-only and parity-failing.

## Review Follow-Up Applied

Claude noted two non-blocking issues:

- `public_speedup_claim_authorized_count` could be ambiguous.
- No test checked that road-hazard wording preserved `0.230652s`, `3.53x`, and `40k`.

Applied follow-up:

- Added `public_speedup_claims_applied_by_this_packet`.
- Added `test_road_hazard_wording_contains_measured_values`.

## Validation

```bash
PYTHONPATH=src:. python3 -m unittest tests/goal1208_public_wording_decision_after_goal1206_test.py
PYTHONPATH=src:. python3 scripts/goal1208_public_wording_decision_after_goal1206.py
```

Result:

- `Ran 4 tests ... OK`
- packet generation `valid=true`

## Consensus

Codex accepts Goal1208. Claude independently reviewed and returned `ACCEPT`. Gemini was attempted first but was blocked by model capacity. This satisfies the project `2-AI` rule because the external-AI side was completed by Claude.

## Boundary

Goal1208 accepts wording decisions only. Public docs still need a separate sync step and verification before release.
