# RTDL v0.4 Audit Report

Date: 2026-04-10
Status: Gemini whole-line audit complete, final Claude audit pending

## Current Audit Evidence

Whole-line implementation audit package:

- [Goal 212 audit report](../../reports/goal212_v0_4_full_audit_2026-04-10.md)
- [Goal 212 review note](../../reports/goal212_v0_4_full_audit_review_2026-04-10.md)
- [Gemini whole-line audit](../../reports/gemini_goal212_v0_4_full_audit_review_2026-04-10.md)
- [Codex consensus](../../../history/ad_hoc_reviews/2026-04-10-codex-consensus-goal212-v0_4-full-audit.md)

## Current Audit Verdict

Gemini's whole-line verdict is:

- the nearest-neighbor line is internally consistent
- the code/docs/process story is technically honest
- the current `v0.4` line is ready for final release-packaging work

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

## Remaining Release Gate

Per the standing project rule, one more whole-line Claude audit should still be
performed after the `4am` reset before the final release tag is created.
