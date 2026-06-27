# Goal4240 Major Performance Target Map After RayJoin Long-Repeat

Date: 2026-06-09

Status: internal direction map accepted with boundary

## Purpose

Goal4240 refreshes the current major performance target map after Goal4239
added dedicated RayJoin long-repeat evidence at current source commit `048d940c`.

This remains a planning map, not a release packet and not a public performance
table.

## Updated Reading

| Target | Status | Updated Reading |
| --- | --- | --- |
| Ten-app current route health | `done_internal_evidence` | Goal4235 proves all ten current front doors pass on RTX 4000 Ada at clean commit `72690687`. |
| Ten-app measurement adequacy closure | `done_internal_evidence` | Goal4230 proves every promoted app has at least one second-level measurement source. |
| RayJoin contract-split route policy | `done_internal_evidence` | Goal4239 now supplies a dedicated 20.76s RayJoin long-repeat profile: PIP one-shot remains Numba; repeated PIP, LSI, and overlay active-count remain prepared RTDL/OptiX routes. |
| RT-DBSCAN profile-aware boundary policy | `done_internal_evidence` | Goal4222 keeps unblocked single-pass as the current default and blocked grouped stream explicit/profile-specific. |
| Prepared-session residency surface | `available_explicit_not_default` | Reuse remains explicit and user-owned. |
| Release packet and public claim review | `needs_broader_evidence` | Current-head execution, measurement adequacy, and RayJoin long-repeat evidence are internally stronger, but exact claims/docs/consensus/hardware still gate release. |
| AMD/HIPRT functional parity | `blocked_pending_hardware` | AMD evidence still requires real AMD hardware. |
| Major release candidate packet | `pending_user_release_decision` | A formal release packet still requires user request plus docs and multi-AI consensus. |

## Boundary

Goal4240 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, automatic partner selection, AMD performance wording, or
app-specific native-engine logic.
