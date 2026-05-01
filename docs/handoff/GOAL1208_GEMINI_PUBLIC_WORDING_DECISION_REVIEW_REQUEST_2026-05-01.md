# Goal1208 Gemini Review Request: Public Wording Decision After Goal1206

Please review the Goal1208 public wording decision packet before any public docs are changed.

## Files To Review

- `scripts/goal1208_public_wording_decision_after_goal1206.py`
- `tests/goal1208_public_wording_decision_after_goal1206_test.py`
- `docs/reports/goal1208_public_wording_decision_after_goal1206_2026-05-01.md`
- `docs/reports/goal1208_public_wording_decision_after_goal1206_2026-05-01.json`
- Source evidence:
  - `docs/reports/goal1206_two_ai_consensus_2026-05-01.md`
  - `docs/reports/goal1206_repaired_rtx_recovery_merge_intake_2026-05-01.md`

## Proposed Decisions

- `road_hazard_screening`: propose bounded reviewed wording because Goal1206 has same-scale floor-safe evidence: OptiX `0.230652s`, Embree `0.814722s`, ratio `3.53x`.
- `database_analytics`: keep positive speedup wording blocked. It is repaired at 100k/300k, but ratios are `1.12x` and `1.16x`, below the `1.2x` public threshold.
- `polygon_set_jaccard`: correctness/readiness only. Public-safe chunk 512 passes parity, but no speedup wording is authorized and chunk 64 remains diagnostic-only/parity-failing.

## Questions

1. Are these public wording decisions conservative and technically justified by Goal1206?
2. Is it correct to promote only `road_hazard_screening` to reviewed positive wording?
3. Is it correct to keep DB speedup wording blocked despite repaired OptiX operation because the ratio is below threshold?
4. Is the Jaccard correctness-only wording narrow enough?
5. Verdict: `ACCEPT` or `BLOCK`, with required fixes if blocked.

Please write the review to:

`docs/reports/goal1208_gemini_public_wording_decision_review_2026-05-01.md`
