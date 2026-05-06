# Goal1412 v1.5 Documentation Cleanup Consensus

Date: 2026-05-06

Scope: review commit `c14c6ce` and the follow-up wording fix that updates the
public front page and documentation from v1.0-live framing to v1.5-current
release framing while preserving historical v1.0/v0.9.x release packages.

## Review Inputs

- Codex implementation and integration review.
- Claude external review:
  `docs/reports/goal1412_claude_v1_5_docs_release_cleanup_review_2026-05-06.md`.
- Gemini attempted review:
  `docs/reports/goal1412_gemini_v1_5_docs_release_cleanup_review_2026-05-06.md`.
- Gemini 2.5 attempted review:
  `docs/reports/goal1412_gemini_2_5_v1_5_docs_release_cleanup_review_2026-05-06.md`.
- Gemini 0.40.1 external review:
  `docs/reports/goal1412_gemini_0_40_1_v1_5_docs_release_cleanup_review_2026-05-06.md`.

## External Review Status

Claude returned `ACCEPT`, found no blocking issues, and confirmed the required
release boundaries:

- v1.5 is described as released, not as a candidate.
- Public usage remains source-tree execution; no pip-install support is claimed.
- No whole-app speedup claim is introduced.
- v1.5 is not described as a zero-app-knowledge native-engine release.
- `COLLECT_K_BOUNDED` remains deferred to v1.5.1.

Claude identified one concrete wording cleanup: a residual
`release-candidate package` phrase in the v1.5 audit report. That phrase has
been changed to `release package`.

Gemini did not return a valid review verdict. The first Gemini run hit CLI tool
availability problems and then server capacity failures. The second run using
`--model gemini-2.5-pro` also failed with `RESOURCE_EXHAUSTED` / HTTP 429 model
capacity errors. These artifacts are retained as failed review attempts and do
not count as accepting reviews.

After the Gemini CLI upgrade to `0.40.1`, Gemini returned `VERDICT ACCEPT`,
found no blockers or nonblockers, and confirmed all required boundary checks.

## Consensus Decision

3-AI consensus is reached as Codex plus two independent external AI reviews
(Claude and Gemini 0.40.1). The reviewed documentation cleanup is publishable
after the `release-candidate package` wording fix.

This consensus does not move or retag any release. It only validates the
published documentation cleanup for v1.5.

## Boundary Contract

The public documentation may say:

- v1.5 is the current public release.
- v1.5 completes the standalone RTDL language/runtime milestone for the
  supported Embree+OptiX surface.
- v1.0 remains historical foundation evidence.
- v1.5 excludes row-returning `COLLECT_K_BOUNDED` apps and defers bounded
  collection stabilization to v1.5.1.
- v1.6-v2.0 are the staged partner-mechanism track.

The public documentation must not say:

- v1.5 supports package installation.
- v1.5 proves whole-app speedups.
- v1.5 has a zero-app-knowledge native engine.
- `COLLECT_K_BOUNDED` is stable in v1.5.
- Any new release/tag action is authorized by this consensus.
