# Codex Subagent Review: Phoenix V3 Aggregate 13-Row Release Readiness

Date: 2026-06-22

Reviewer: Codex subagent `Hubble` (`019eed4e-c038-7612-97ff-f7e2b6c3416b`)

Boundary: this is a Codex subagent review. It is read-only and cannot substitute for a Claude/Gemini external release authorization.

## Verdict

`approve_blocked_not_release`

The 13-row / 9-capability surface removes the old missing-Spatial / surface-width blocker. It does not authorize Phoenix V3 release.

## Findings

P0: Release remains unauthorized. The live readiness gate still reports:

- `status: blocked_not_release`
- `release_authorized: false`
- `blocking_reasons: ["release_authorization_false", "updated_thirteen_row_release_readiness_consensus_required"]`

Primary gate:

`docs/rebuild/v3/phoenix_v3_release_readiness_gate_2026-06-21.json`

P0: No external aggregate authorization was obtained. The external-AI blocked record documents the current Claude session-limit failure and Gemini ineligibility, and explicitly says it is not release approval:

`docs/reviews/external_ai_blocked_phoenix_v3_aggregate_release_readiness_13_row_2026-06-22.md`

P1: Claim boundaries remain narrow. The wording gate passes and the current full V3 rebuild matrix is green, but those are prerequisite evidence, not release authorization.

## Confirmed Current Evidence

The breadth gate records:

- total current M7/supplemental release-surface rows: 13
- planned capability families covered: 9/9
- missing M7 capability families: none

The new Spatial supplemental row is:

`point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7`

Full V3 rebuild evidence:

`docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_spatial_default_path_m7_20260622.json`

Summary:

```text
100 modules / 486 tests OK
```

## Required Fix Before Release

Obtain a fresh Claude or Gemini aggregate release-readiness review over the current 13-row / 9-capability packet. If that review authorizes release, regenerate/update the release-readiness gate accordingly.

Until then:

- keep `release_authorized: false`
- keep strict release failing
- preserve the current wording boundaries

## Exact Release Authorization Statement

Phoenix V3 release is not authorized.

Current authorized statement:

Phoenix V3 has a 13-row, 9-capability row-scoped/supplemental M7 evidence surface, but release remains `blocked_not_release` pending fresh external aggregate release-readiness authorization.

## Exact Non-Authorized Claim Boundaries

Do not claim:

- package-install readiness
- broad hardware portability
- multi-GPU or second-RTX performance portability
- broad V3-faster-than-V2
- public Spatial speedup
- RTDL-beats-RayJoin
- true zero-copy
- V4/C ABI/embedding readiness
- whole-app acceleration
- whole Spatial RayJoin
- whole RayDB
- whole RTNN
- whole Barnes-Hut
- paper reproduction
- release readiness

Only the exact reviewed row-scoped M7 boundaries are supportable.
