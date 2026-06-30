# 3-AI Consensus: Goal 1602 v1.6 Public Docs Overclaim Audit

## Verdict

Consensus is reached.

Goal 1602 is accepted as the first local public-docs overclaim audit for the
`v1.6` Python+RTDL closure path.

This consensus does not authorize `v1.6` release, release-tag action, public
speedup wording, whole-app speedup wording, broad RTX/GPU acceleration wording,
true zero-copy wording, partner support claims, package-install claims, or
stable `COLLECT_K_BOUNDED` promotion.

## Reviewed Artifacts

- Patched public architecture page:
  `docs/current_architecture.md`
- Codex audit report:
  `docs/reports/goal1602_v1_6_public_docs_overclaim_audit_2026-05-09.md`
- Audit regression test:
  `tests/goal1602_v1_6_public_docs_overclaim_audit_test.py`
- Claude review:
  `docs/reviews/goal1602_v1_6_public_docs_overclaim_audit_claude_review_2026-05-09.md`
- Gemini review:
  `docs/reviews/goal1602_v1_6_public_docs_overclaim_audit_gemini_review_2026-05-09.md`

## Consensus Positions

Codex position:

The front-door public docs mostly preserved the required claim boundaries, but
`docs/current_architecture.md` had stale roadmap wording that grouped `v1.6`
with the partner-mechanism track. The patch realigns the public architecture
page with the accepted roadmap: `v1.6` closes Python+RTDL, while `v1.7-v2.0`
is the Python+partner+RTDL track.

Claude position:

Claude returned `ACCEPT` as a public-docs overclaim audit artifact, not release
authorization. Claude confirmed that the stale roadmap drift was correctly
identified and fixed, and that the report disclaims the prohibited outcomes.
Claude suggested stronger future-proofing: wider forbidden release-claim
phrases and per-file findings. Those non-blocking suggestions were applied
before this consensus file was written.

Gemini position:

Gemini returned `ACCEPTED`, verified that the roadmap boundary is correct, and
confirmed that the public docs do not leak unauthorized RT-core speedup,
whole-app acceleration, zero-copy, or stable `COLLECT_K_BOUNDED` claims.

## Accepted Findings

- `docs/current_architecture.md` is now aligned with the accepted `v1.6`
  roadmap.
- Current front-door docs do not publish `v1.6`.
- Current front-door docs do not authorize whole-app speedup, broad RT-core
  speedup, true zero-copy, partner support, package-install support, or stable
  `COLLECT_K_BOUNDED` promotion.
- Historical v1.5 release-package files remain audit/history artifacts and
  were not rewritten as current `v1.6` release docs.

## Validation

Windows audit/readiness/proposal slice:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal1602_v1_6_public_docs_overclaim_audit_test `
  tests.goal1601_v1_6_release_surface_proposal_test `
  tests.goal1600_v1_6_python_rtdl_readiness_gate_test
```

Result:

- `Ran 15 tests`
- `OK`

## Decision

Accept Goal 1602 as the first public-docs overclaim audit closure artifact for
the `v1.6` path.

Proceed next to the stable native-path app-leakage audit.

Do not publish `v1.6` yet.
