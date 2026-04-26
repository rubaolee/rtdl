# Goal1006 External Review Request

Please independently review Goal1006, a strict public RTX claim wording gate over the Goal1005 final A5000 candidate set.

## Files

- Script: `scripts/goal1006_public_rtx_claim_wording_gate.py`
- Tests: `tests/goal1006_public_rtx_claim_wording_gate_test.py`
- JSON report: `docs/reports/goal1006_public_rtx_claim_wording_gate_2026-04-26.json`
- Markdown report: `docs/reports/goal1006_public_rtx_claim_wording_gate_2026-04-26.md`
- Source candidate audit: `docs/reports/goal1005_post_a5000_speedup_candidate_audit_2026-04-26.json`

## Policy Being Reviewed

Goal1006 does not authorize public speedup claims. It only identifies rows mature enough to send to a later 2-AI public wording review.

The gate requires:

- Goal1005 candidate status,
- fastest-baseline/RTX ratio >= 1.20,
- comparable RTX phase >= 0.10 s,
- no whole-app wording.

Current result:

- `1` public-review-ready query-phase row: `service_coverage_gaps / prepared_gap_summary`
- `7` candidates held for larger-scale repeat because their RTX phases are under 10 ms
- `9` non-candidate rows
- `0` public speedup claims authorized

## Review Questions

1. Is the 100 ms minimum phase-duration rule reasonable for preventing fragile microbenchmark wording?
2. Is it correct that only `service_coverage_gaps / prepared_gap_summary` is public-review-ready under this policy?
3. Does the allowed wording stay bounded to a measured query phase and avoid whole-app claims?
4. Are the held/rejected rows conservatively handled?

## Expected Output

Write `ACCEPT` or `BLOCK` with concrete findings. If writing to repo is available, save to `docs/reports/goal1006_<reviewer>_external_review_2026-04-26.md`.
