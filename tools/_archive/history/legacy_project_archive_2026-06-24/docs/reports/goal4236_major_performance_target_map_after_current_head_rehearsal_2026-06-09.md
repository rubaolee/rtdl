# Goal4236 Major Performance Target Map After Current-Head Rehearsal

Date: 2026-06-09

Status: internal direction map accepted with boundary

## Purpose

Goal4236 refreshes the current major performance target map after Goal4235
proved that all ten promoted benchmark front doors still pass on a clean RTX
4000 Ada pod at source commit `72690687`.

This is a planning map, not a release packet and not a public performance table.

## Current Target Map

| Target | Status | Reading | Next Action |
| --- | --- | --- | --- |
| Ten-app current route health | `done_internal_evidence` | Goal4235 proves all ten current front doors pass on RTX 4000 Ada at clean commit `72690687`. | Use as the latest internal health packet only. |
| Ten-app measurement adequacy closure | `done_internal_evidence` | Goal4230 reconciles Goal4185/4186/4189/4225/4228/4229 and shows all ten promoted apps have second-level measurement evidence above the one-second hot-path or representative-profile floor. | Use as internal measurement-readiness evidence only. |
| RayJoin contract-split route policy | `done_internal_evidence` | Goals4218 and 4223 show PIP one-shot favors Numba, while LSI and overlay scalar-count/active-count contracts favor prepared RTDL/OptiX across bounded public-CDB slices. | Keep the contract split visible; do not collapse it into one RayJoin paper-reproduction number. |
| RT-DBSCAN profile-aware boundary policy | `done_internal_evidence` | Goal4222 shows unblocked single-pass grouped stream beats blocked grouped stream on clustered3d, road3d, and ngsim_dense at 65k and 262k. | Keep unblocked as current default; keep blocked explicit/profile-specific. |
| Prepared-session residency surface | `available_explicit_not_default` | Explicit cache keys, invalidation, timing, tutorial, and helper already exist. | Improve ergonomics only without hidden global cache or automatic backend/partner choice. |
| Release packet and public claim review | `needs_broader_evidence` | Current-head execution and measurement adequacy are internally closed, but public release claims still need exact wording, docs audit, and fresh multi-AI consensus. | Assemble a formal release packet only if requested; run extra long timing only if the release claim needs a public performance table. |
| AMD/HIPRT functional parity | `blocked_pending_hardware` | NVIDIA/OptiX current routes are healthy; AMD evidence requires AMD hardware. | Run HIPRT functional parity first when AMD pod exists. |
| Major release candidate packet | `pending_user_release_decision` | Current NVIDIA internal evidence is strong but non-authorizing. | User-requested release packet plus docs and multi-AI consensus required. |

## Boundary

Goal4236 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, automatic partner selection, AMD performance wording, or
app-specific native-engine logic.
