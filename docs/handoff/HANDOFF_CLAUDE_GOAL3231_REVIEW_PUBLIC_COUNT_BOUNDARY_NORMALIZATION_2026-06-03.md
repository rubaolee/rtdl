# Handoff: Claude Review for Goal3230 Public Count Boundary Normalization

Please perform an independent read-only review of Goal3230 and write the review to:

`docs/reviews/goal3231_claude_review_goal3230_public_count_boundary_normalization_2026-06-03.md`

## Scope

Review the work through commit `c46e8738`:

- `scripts/goal3225_rayjoin_public_overlay_active_count_probe.py`
- `scripts/goal3227_rayjoin_public_pip_count_probe.py`
- `docs/reports/goal3225_rayjoin_public_overlay_active_count_probe_2026-06-03.{json,md,stdout}`
- `docs/reports/goal3227_rayjoin_public_pip_count_probe_2026-06-03.{json,md,stdout}`
- `docs/reports/goal3229_rayjoin_public_count_coverage_summary_2026-06-03.md`
- `docs/reports/goal3230_rayjoin_public_count_claim_boundary_normalization_2026-06-03.md`
- `tests/goal3225_rayjoin_public_overlay_active_count_probe_artifact_test.py`
- `tests/goal3227_rayjoin_public_pip_count_probe_artifact_test.py`
- `tests/goal3230_rayjoin_public_count_claim_boundary_normalization_test.py`

## Questions To Answer

1. Does Goal3230 really close the Goal3226/Goal3228 informational inconsistency by normalizing top-level, row-level, and measurement-level claim-boundary keys to the same six canonical false flags?
2. Do the refreshed pod artifacts at commit `92e16b8649f99aa62fbca0d0c97466a7a2f8eaa3` preserve the same count contracts and observed counts (`1`, `9`, and `1430`)?
3. Do the reports and tests avoid authorizing release, public speedup, broad RT-core speedup, true zero-copy, `RTDL beats RayJoin`, or RayJoin paper-reproduction claims?
4. Are there any remaining machine-checkability or wording issues that should be fixed before this public-count evidence is used by later RayJoin planning reports?

## Suggested Validation

Run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3225_rayjoin_public_overlay_active_count_probe_test tests.goal3227_rayjoin_public_pip_count_probe_test tests.goal3225_rayjoin_public_overlay_active_count_probe_artifact_test tests.goal3227_rayjoin_public_pip_count_probe_artifact_test tests.goal3229_rayjoin_public_count_coverage_summary_test tests.goal3230_rayjoin_public_count_claim_boundary_normalization_test
```

## Required Review Shape

Use a verdict of `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Lead with findings by severity. If no blocking findings exist, say so clearly. Keep the release boundary explicit: this review must not authorize release, public speedup, broad RT-core speedup, true zero-copy, `RTDL beats RayJoin`, or RayJoin paper-reproduction claims.
