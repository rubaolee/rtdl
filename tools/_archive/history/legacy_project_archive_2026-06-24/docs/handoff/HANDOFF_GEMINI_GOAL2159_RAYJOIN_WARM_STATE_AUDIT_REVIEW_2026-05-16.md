# Handoff: Gemini Review For Goal2159 RayJoin Warm-State Audit

Please perform an independent read-only Gemini review of Goal2159.

## Context

Goal2159 turns the earlier one-off RayJoin public CDB LSI measurements into a reusable committed runner and, more importantly, corrects the public interpretation of the Goal2157 nonzero-LSI performance result.

The key issue is warm-state sensitivity:

- Running `lsi_county256_soil256_count192` alone through the committed runner gives the conservative median:
  - CPU `0.016228` sec
  - Embree `0.030806` sec
  - OptiX `0.015426` sec
  - OptiX vs CPU about `1.05x`
  - OptiX vs Embree about `2.00x`
- Running `lsi_county256_soil256_count128` first and then `count192` in the same process reproduces a much faster OptiX state:
  - `count192` OptiX median about `0.003090` sec
  - OptiX vs CPU about `5.28x`
  - OptiX vs Embree about `6.25x`

Goal2159 intentionally narrows the public claim to the conservative single-case runner result unless a future protocol explicitly defines multi-case warmed OptiX state.

## Files To Review

- `scripts/goal2159_rayjoin_public_cdb_runner.py`
- `tests/goal2159_rayjoin_public_cdb_runner_test.py`
- `docs/reports/goal2157_rayjoin_public_cdb_nonzero_lsi_slice_evidence_2026-05-16.md`
- `docs/reports/goal2159_rayjoin_public_cdb_runner_and_warm_state_audit_2026-05-16.md`
- `docs/reports/goal2159_rayjoin_public_cdb_runner_count192_pod_2026-05-16.json`
- `docs/reports/goal2159_rayjoin_public_cdb_runner_count128_192_pod_2026-05-16.json`
- `tests/goal2159_rayjoin_public_cdb_runner_and_warm_state_audit_test.py`

## Review Questions

1. Does the committed runner provide a reproducible and bounded RayJoin public-CDB benchmark protocol?
2. Does the Goal2159 report correctly narrow the public performance interpretation and avoid overclaiming the 5x warm-state number?
3. Are the claim-boundary flags and text conservative enough for v2.0 release preparation?
4. Do the tests guard the correction and artifact assumptions adequately?
5. Does this remain consistent with the RTDL v2.0 rule that public performance claims require exact scope, same-contract comparison, and reviewed evidence?

## Output Request

Write the review to:

`docs/reviews/goal2160_gemini_review_goal2159_rayjoin_warm_state_audit_2026-05-16.md`

Use one of these verdict values:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please explicitly state that this is an independent Gemini review, distinct from Codex, and that it does not authorize v2.0 release by itself.
