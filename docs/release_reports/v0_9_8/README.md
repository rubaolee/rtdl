# RTDL v0.9.8 Release Package

Status: released as `v0.9.8`.

`v0.9.8` is the bounded RTX app evidence and public-claim cleanup release. It
packages the post-`v0.9.6` work that tightened application-level NVIDIA RTX
claim boundaries, repaired stale audit expectations, and added reviewed public
wording for one additional prepared native RTX sub-path.

## Scope

This release package records the surface after `v0.9.6`:

- v0.9.6 prepared/prepacked visibility-count work remains the backend baseline
  under the released v0.9.8 app-claim cleanup package.
- Public RTX app wording is synchronized to `11` reviewed sub-path rows.
- `road_hazard_screening / prepared_native_compact_summary_40k` is the only new
  reviewed public RTX speedup wording row in this release window.
- `database_analytics` and `polygon_set_jaccard` remain blocked from public
  speedup wording.
- Goal1214 full local discovery evidence: `2366` tests OK,
  `196` skips, `0` failures, `0` errors.
- The current release-surface documentation evidence is Goal1215: `64` tests
  OK.
- Goal1216 confirms local release-candidate readiness.
- Goal1217 repaired the live `VERSION` marker back to the public baseline
  `v0.9.6` before the v0.9.8 release action.
- Goal1218 confirms no additional pod run is needed before release package and
  authorization paperwork.

## Boundary

Allowed conclusion:

> RTDL `v0.9.8` is a bounded RTX app evidence and public-claim cleanup release.
> Its new public speedup wording is limited to the prepared
> native road-hazard compact-summary traversal/count sub-path at 40k copies.

Disallowed conclusions:

- a broad whole-app RTDL speedup claim;
- a broad NVIDIA RT-core speedup claim for every app;
- public speedup wording for `database_analytics`;
- public speedup wording for `polygon_set_jaccard`;
- default road-hazard app, GIS/routing, row-output, or Python orchestration
  speedup;
- new HIPRT/AMD GPU validation;
- release scope beyond the audited v0.9.8 package.

## Start Here

- [Release Statement](release_statement.md)
- [Support Matrix](support_matrix.md)
- [Audit Report](audit_report.md)
- [Tag Preparation](tag_preparation.md)
- [v1 RTX App Status](../../v1_0_rtx_app_status.md)
- [Goal1216 Release-Candidate Audit](../../reports/goal1216_v0_9_8_release_candidate_audit_2026-05-01.md)
- [Goal1217 Version Marker Sync](../../reports/goal1217_version_marker_current_release_sync_2026-05-01.md)
- [Goal1218 Release-Authorization Gate](../../reports/goal1218_v0_9_8_release_authorization_gate_2026-05-01.md)

## Latest Gate Evidence

- full local discovery: `2366` tests OK, `196` skips
- release-surface docs: `64` tests OK
- Goal1216 release-candidate audit: valid
- Goal1217 version-marker sync: accepted by Gemini and Codex
- Goal1218 authorization gate: valid evidence
- Goal1219 release package review: accepted by Gemini and Codex
- Goal1220 final authorization: accepted by Gemini and Codex

## Release State

This package is the released `v0.9.8` public boundary after final authorization
and release action.
