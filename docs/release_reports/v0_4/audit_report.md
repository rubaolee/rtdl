# RTDL v0.4 Audit Report

Date: 2026-04-10
Status: whole-line audits complete; later heavy benchmark follow-up preserved

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
- the current `v0.4` line is technically ready for final user-authorized
  release closure once the later heavy benchmark evidence is included as part of
  the live package truth

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

## Important Late-Line Finding Preserved In The Audit Trail

The most important late-line correctness event after the whole-line audit was:

- Goal 228 heavy Linux benchmarking exposed a real shared accelerated
  `fixed_radius_neighbors` boundary bug
- the first heavy run showed:
  - CPU and indexed PostGIS: `45632` rows
  - Embree, OptiX, Vulkan: `45626` rows
- Goal 229 traced the issue to float-path candidate loss on large coordinates
- the accelerated paths were repaired and the heavy Linux rerun now shows:
  - CPU, Embree, OptiX, Vulkan, and indexed PostGIS: `45632` rows

That event is now part of the live release truth and should not be omitted from
the final `v0.4` packaging story.

## Release Gate Result

The whole-line audit gate is closed, with the later heavy-case follow-up
preserved:

- Gemini audit completed
- Claude audit completed
- Claude's two stale-label findings were fixed before any tag creation
- the later Goal 228 heavy benchmark is preserved
- the later Goal 229 boundary fix is preserved
