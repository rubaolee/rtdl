# Handoff: Claude Review Goal3240

Please perform an independent read-only review of the latest RayJoin upstream
build / same-slice smoke chain.

## Scope

Review these RTDL commits and artifacts:

- `e18d1c2c` — Goal3237 intake row-continuation review cleanup.
- `edc07344` — refreshed Goal3232 row-continuation artifact after cleanup.
- `4718dd17` — Goal3239 upstream RayJoin build and same-slice smoke.

Primary files:

- `docs/reviews/goal3237_claude_review_hardened_rayjoin_row_continuation_chain_2026-06-03.md`
- `docs/reports/goal3232_rayjoin_public_row_continuation_probe_2026-06-03.md`
- `docs/reports/goal3232_rayjoin_public_row_continuation_probe_2026-06-03.json`
- `docs/reports/goal3238_rayjoin_public_evidence_status_after_row_continuation_2026-06-03.md`
- `docs/reports/goal3239_rayjoin_upstream_build_and_same_slice_smoke_2026-06-03.md`
- `docs/reports/goal3239_rayjoin_upstream_build_and_same_slice_smoke_2026-06-03.json`
- `tests/goal3232_rayjoin_public_row_continuation_probe_artifact_test.py`
- `tests/goal3239_rayjoin_upstream_build_and_same_slice_smoke_test.py`

## Questions

1. Does Goal3237 intake fully resolve your prior Goal3237 findings: stale
   Goal3234 timing text, redundant PIP CPU summary count, and refreshed artifact
   provenance?
2. Is the refreshed Goal3232 artifact machine-consistent with the report and
   tests, including commit `e18d1c2c`, four public row cases, zero symmetric
   differences, LSI coordinate delta `0`, and no `positive_assignments_count`
   duplicate?
3. Is Goal3239 honest about upstream RayJoin build conditions: two local CUDA
   12.8 compatibility shims, both executables built, LSI RT same-slice agreement
   at 269 rows, PIP as timing/check smoke only, and overlay RT blocked by an
   upstream runtime failure?
4. Does Goal3239 preserve all claim boundaries: no release, no public speedup,
   no broad RT-core speedup, no true zero-copy, no `RTDL beats RayJoin`, and no
   RayJoin paper-reproduction claim?
5. What are the required next engineering steps before this can become a real
   same-contract RayJoin comparison rather than a smoke?

## Output

Write your review to:

`docs/reviews/goal3240_claude_review_rayjoin_upstream_build_smoke_2026-06-03.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
Lead with findings by severity. Keep the release boundary explicit.
