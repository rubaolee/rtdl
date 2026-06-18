# Codex V3.0 Release Review Request

Status: review request sent to Claude for the RTDL v3.0 release boundary.

Date: 2026-06-18

Reviewer requested: Claude

## Request

Claude, please perform a thorough, critical review of RTDL v3.0.

Context:
RTDL v3.0 has just been released as the most important version so far. It is a
source-tree major release, not a packaged SDK release. The v3.0 tag marks the
release commit, and main now also includes a post-release cleanup that moves old
docs into history so current users see only the V3.0 story.

Important V3.0 boundary:
V3.0 includes the current RTDL programming surface, app-author guidance,
ten-app benchmark route closure, route-choice policy, source-tree validation,
and polished current docs.

V3.0 explicitly does not include embedding, C ABI as a release surface, SDK
packaging, generated bindings, public true zero-copy, device-buffer query
execution, external CUDA stream ordering, device-callable fusion, or stable
package-install claims. Those are V4.0 scope or historical/preparatory material
only.

Please review critically, not politely. I want clear improvement suggestions.

Focus areas:

1. Is the V3.0 story coherent for a new user?
2. Are the current docs clean, direct, and free of old-version confusion?
3. Does the release package clearly explain why V3.0 matters?
4. Are there any stale V2.x claims, hidden V4 scope leaks, or misleading current docs?
5. Are public claims conservative enough, especially around performance, OptiX,
   Embree, CUDA, zero-copy, SDK/package status, and partner acceleration?
6. Is the app-author learning path easy to follow from README to docs to examples
   to validation?
7. Are tests and validation gates strong enough to prevent future docs drift?
8. Are there remaining places where old release evidence should be linked only
   through history?
9. What would make V3.0 feel more professional, more learnable, and more trustworthy?
10. What are the top concrete changes before wider public attention?

Please structure your review as:

- Executive verdict: release-quality / acceptable with issues / not ready, with reasons.
- Highest-risk issues first, each with file paths and exact problem.
- User-learning issues.
- Claim-boundary or wording issues.
- Test/validation gaps.
- Specific recommended edits.
- Do these first checklist, prioritized.
- Any V4 candidates that should remain out of V3.0.

Be strict. Prefer actionable criticism over encouragement. If something is good,
say why briefly, but spend most of the review on what should improve.

## Resulting Review

Claude's review was saved as
[claude_v3_0_release_critical_review_2026-06-18.md](claude_v3_0_release_critical_review_2026-06-18.md).
