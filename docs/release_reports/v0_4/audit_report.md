# RTDL v0.4 Audit Report

Date: 2026-04-10
Status: whole-line audits complete; later heavy benchmark follow-up preserved

## Current Audit Evidence

Whole-line implementation audit package:

- [Whole-line audit report](../../reports/goal212_v0_4_full_audit_2026-04-10.md)
- [Whole-line audit review note](../../reports/goal212_v0_4_full_audit_review_2026-04-10.md)
- [Gemini whole-line audit](../../reports/gemini_goal212_v0_4_full_audit_review_2026-04-10.md)
- [Claude whole-line audit](../../reports/claude_goal212_v0_4_full_audit_review_2026-04-10.md)
- [Codex consensus](../../../history/ad_hoc_reviews/2026-04-10-codex-consensus-goal212-v0_4-full-audit.md)
- [Heavy benchmark report](../../reports/goal228_v0_4_heavy_nearest_neighbor_perf_2026-04-10.md)
- [Accelerated boundary-fix report](../../reports/goal229_fixed_radius_neighbors_accelerated_boundary_fix_2026-04-10.md)
- [Final pre-release verification report](../../reports/goal232_final_pre_release_verification_2026-04-10.md)

## Current Audit Verdict

Whole-line audit verdict:

- the nearest-neighbor line is internally consistent
- the code/docs/process story is technically honest
- the released `v0.4.0` line includes the later heavy benchmark evidence as
  part of the live package truth

## Important Mid-Line Finding Preserved In The Audit Trail

The most important late-line correctness event in `v0.4` was:

- scaling work exposed a real Embree bug in `fixed_radius_neighbors`
- the bug was that `g_query_kind` was not set before the point-query call,
  which caused silent zero-row behavior on some valid cases
- this was fixed in `src/native/embree/rtdl_embree_api.cpp`
- the relevant Embree tests were rerun and passed after the repair

That event strengthens the audit story rather than weakening it, because the
whole-line process actually surfaced and fixed a real backend defect before
release.

## Important Late-Line Finding Preserved In The Audit Trail

The most important late-line correctness event after the whole-line audit was:

- heavy Linux benchmarking exposed a real shared accelerated
  `fixed_radius_neighbors` boundary bug
- the first heavy run showed:
  - CPU and indexed PostGIS: `45632` rows
  - Embree, OptiX, Vulkan: `45626` rows
- the follow-up boundary fix traced the issue to float-path candidate loss on
  large coordinates
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
- the later heavy benchmark is preserved
- the later accelerated boundary fix is preserved
- the clean release-prep worktree full verification run is preserved:
  - `Ran 525 tests in 116.882s`
  - `OK (skipped=59)`

## Final 2026-04-11 Review Gate Closure

The final technical release gate was closed following a comprehensive audit of the clean release-prep workspace:

- [Final total code review](../../reports/gemini_v0_4_total_code_review_2026-04-11.md): **PASS**
- [Final total doc review](../../reports/gemini_v0_4_total_doc_review_2026-04-11.md): **PASS**
- [Final detailed process audit](../../reports/gemini_v0_4_detailed_process_audit_2026-04-11.md): **PASS**
- [Final public-surface cleanup review](../../reports/gemini_goal239_final_public_surface_cleanup_review_2026-04-11.md): **PASS**

**Audit Finality**:
All blocking findings have been resolved, maintainer-local context has been scrubbed, and the `v0.4.0` identity is consistently presented across the live documentation surface.

**Release Conclusion**:
- [Gemini final review-closure note](../../reports/gemini_v0_4_final_review_closure_2026-04-11.md)
- Verdict: **RELEASE AUTHORIZED AND PUBLISHED AS `v0.4.0`**
