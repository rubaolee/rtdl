# Handoff: Claude Review for Hardened RayJoin Row-Continuation Chain

Please perform an independent read-only review and write it to:

`docs/reviews/goal3237_claude_review_hardened_rayjoin_row_continuation_chain_2026-06-03.md`

## Scope

Review the current chain through commit `3e4b4891`:

- Goal3232 public row-continuation harness and refreshed artifact.
- Goal3234 public overlay row-scale addendum.
- Goal3235 intake of the prior Goal3233 Claude review.
- Goal3236 extension of Goal3232 to cover public LSI row continuation.

Primary files:

- `scripts/goal3232_rayjoin_public_row_continuation_probe.py`
- `docs/reports/goal3232_rayjoin_public_row_continuation_probe_2026-06-03.{json,md,stdout}`
- `docs/reports/goal3234_rayjoin_public_overlay_row_scale_addendum_2026-06-03.{json,md,stdout}`
- `docs/reports/goal3235_claude_review_intake_row_continuation_hardening_2026-06-03.md`
- `docs/reviews/goal3233_claude_review_goal3232_public_rayjoin_row_continuation_2026-06-03.md`
- `tests/goal3232_rayjoin_public_row_continuation_probe_test.py`
- `tests/goal3232_rayjoin_public_row_continuation_probe_artifact_test.py`
- `tests/goal3234_rayjoin_public_overlay_row_scale_addendum_test.py`
- `tests/goal3235_claude_review_intake_row_continuation_hardening_test.py`

## Review Questions

1. Does the updated Goal3232 artifact now validate public row continuation for all three current RayJoin row families: PIP, LSI, and overlay?
2. Does the LSI validation correctly compare segment-pair IDs and record `max_lsi_coordinate_delta = 0` without adding app-specific native engine logic?
3. Did the Goal3235 changes adequately address the prior Goal3233 advisory findings: positive-only PIP membership, named-phase overhead visibility, single-repeat boundary, and CPU summary compaction?
4. Does the Goal3234 scale addendum remain valid after the Goal3235/3236 changes, and does it preserve the public-claim boundary?
5. Are there any remaining wording, machine-checkability, artifact-size, or methodology issues that should be fixed before using this row-continuation evidence in a RayJoin planning/status report?

## Suggested Validation

Run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3232_rayjoin_public_row_continuation_probe_test tests.goal3232_rayjoin_public_row_continuation_probe_artifact_test tests.goal3234_rayjoin_public_overlay_row_scale_addendum_test tests.goal3235_claude_review_intake_row_continuation_hardening_test
```

## Required Review Shape

Use a verdict of `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Lead with findings by severity. Keep the release boundary explicit: this review must not authorize release, public speedup, broad RT-core speedup, true zero-copy, `RTDL beats RayJoin`, or RayJoin paper-reproduction claims.
