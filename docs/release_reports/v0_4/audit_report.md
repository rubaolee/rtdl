# RTDL v0.4 Audit Report

Date: 2026-04-10
Status: Gemini and Claude whole-line audits complete

## Current Audit Evidence

Whole-line implementation audit package:

- [Goal 212 audit report](../../reports/goal212_v0_4_full_audit_2026-04-10.md)
- [Goal 212 review note](../../reports/goal212_v0_4_full_audit_review_2026-04-10.md)
- [Gemini whole-line audit](../../reports/gemini_goal212_v0_4_full_audit_review_2026-04-10.md)
- [Claude whole-line audit](../../reports/claude_goal212_v0_4_full_audit_review_2026-04-10.md)
- [Codex consensus](../../../history/ad_hoc_reviews/2026-04-10-codex-consensus-goal212-v0_4-full-audit.md)

## Current Audit Verdict

Whole-line audit verdict:

- the nearest-neighbor line is internally consistent
- the code/docs/process story is technically honest
- the current `v0.4` line is ready for final user-authorized release closure

## Important Mid-Line Finding Preserved In The Audit Trail

The most important late-line correctness event in `v0.4` was:

- Goal 209 scaling work exposed a real Embree bug in
  `fixed_radius_neighbors`
- the bug was that `g_query_kind` was not set before the point-query call,
  which caused silent zero-row behavior on some valid cases
- this was fixed in `src/native/embree/rtdl_embree_api.cpp`
- the relevant Embree tests were rerun and passed after the repair

That event strengthens the audit story rather than weakening it, because the
whole-line process actually surfaced and fixed a real backend defect before
release.

## Release Gate Result

The whole-line audit gate is closed:

- Gemini audit completed
- Claude audit completed
- Claude's two stale-label findings were fixed before any tag creation
