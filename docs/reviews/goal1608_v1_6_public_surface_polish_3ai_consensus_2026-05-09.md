# Goal1608 v1.6 Public Surface Polish 3-AI Consensus

Date: 2026-05-09

## Scope

Review of the v1.6 public user surface after the release tag:

- front page
- tutorials
- docs index and public map
- release-facing examples and examples index
- public performance/claim boundary wording
- regression tests for public-surface consistency

## Codex Verdict

ACCEPT.

Codex updated the public entry points so v1.6 is presented as the current
release, the first Python+RTDL architecture milestone, and the current
source-tree usage boundary. The edits preserve the standing non-claims:

- no package-install support claim
- no whole-app speedup claim
- no `--backend optix` equals RT-core speedup claim
- no `COLLECT_K_BOUNDED` stable-promotion claim
- no true zero-copy claim

## Claude Verdict

ACCEPT.

Claude reviewed the diff and found no blockers. Claude specifically accepted
the v1.5-to-v1.6 wording update, the source-tree command clarity, the OptiX and
whole-app speedup boundaries, and the continued deferral of
`COLLECT_K_BOUNDED`.

Review file:

- `docs/reviews/goal1608_v1_6_public_surface_polish_claude_review_2026-05-09.md`

## Gemini Verdict

ACCEPT.

Gemini reviewed the diff and found no blockers. Gemini specifically accepted
the v1.6 architecture-milestone framing, platform-specific command clarity,
historical treatment of older releases, and the updated regression-test
coverage.

Review file:

- `docs/reviews/goal1608_v1_6_public_surface_polish_gemini_review_2026-05-09.md`

## Consensus

The v1.6 public front page, tutorials, docs, and examples are consistent enough
to publish on `main`.

This consensus does not authorize a new release tag, retag, performance claim,
package-install claim, true zero-copy claim, or stable `COLLECT_K_BOUNDED`
promotion.
