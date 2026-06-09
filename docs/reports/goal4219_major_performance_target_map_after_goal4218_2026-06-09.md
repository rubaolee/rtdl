# Goal4219 Major Performance Target Map After Goal4218

Date: 2026-06-09

Status: internal direction map accepted with boundary

## Purpose

Goal4219 records the major performance direction after the Goal4215 all-app
health packet and the Goal4218 focused RayJoin/RT-DBSCAN mixed-route packet.

The purpose is to keep the project focused on language/runtime improvements,
not app micro-tuning. RTDL remains a generic app-agnostic runtime with explicit
user partner choice. Benchmark apps are pressure tests and reference
implementations; they do not justify app-specific native-engine logic.

## What Changed

Added `src/rtdsl/current_major_performance_targets.py` with:

- `current_major_performance_targets()`
- `summarize_current_major_performance_targets()`
- `validate_current_major_performance_targets()`

The API is exported from `rtdsl.__init__`, alongside the existing current
benchmark front-door, scale-profile, route-decision, and adequacy registries.

## Current Target Map

| Target | Status | Reading | Next Action |
| --- | --- | --- | --- |
| Ten-app current route health | `done_internal_evidence` | Goal4215 proves all ten current front doors pass on RTX 4000 Ada at `63289bbc`. | Use as internal health packet only; not a release/performance table. |
| RayJoin contract-split route policy | `needs_broader_evidence` | Goal4218 confirms bounded PIP one-shot favors Numba while repeated PIP, LSI, and overlay favor RTDL/OptiX. | Use larger/non-dense same-contract evidence before any broader wording. |
| RT-DBSCAN profile-aware boundary policy | `needs_broader_evidence` | Goal4218 shows unblocked canonical single-pass is about `4.5x` faster than blocked on current 65k clustered3d. | Spend pod time only on broader profile/scale evidence or advisor logic. |
| Prepared-session residency surface | `available_explicit_not_default` | Explicit cache keys, invalidation, timing, tutorial, and helper already exist; cache remains user-owned. | Improve ergonomics only without hidden global cache or auto backend/partner choice. |
| AMD/HIPRT functional parity | `blocked_pending_hardware` | NVIDIA/OptiX current routes are healthy; AMD evidence requires AMD hardware. | Run HIPRT functional parity first when AMD pod exists. |
| Major release candidate packet | `pending_user_release_decision` | Current NVIDIA internal evidence is strong but non-authorizing. | User-requested release packet plus docs and multi-AI consensus required. |

## Design Boundary

This map deliberately does not pick a hidden partner for users. It says where
the current evidence points, but users still choose routes/partners explicitly.
It also does not turn internal RT-core subpath evidence into broad RT-core or
whole-app speedup wording.

## Release Boundary

Goal4219 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, automatic partner selection, AMD performance wording, or
app-specific native-engine logic.
