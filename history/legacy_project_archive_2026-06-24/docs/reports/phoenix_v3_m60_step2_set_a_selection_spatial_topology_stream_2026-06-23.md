# Phoenix V3 M60 Step-2 Set-A Selection: Spatial Topology Stream

Date: 2026-06-23

Status:

```text
m60_spatial_topology_stream_selected_pending_external_review_not_release
```

## Scope

M60 selects the next Phoenix V3 Step-2 Set-A runtime-family target after M59.
It is a planning and review packet only. It does not implement new runtime code,
run POD, run all-app, authorize release, or authorize public performance
wording.

## Decision

Select **Spatial/RayJoin point-location topology stream** as the next Step-2
Set-A runtime-family target, but only in this form:

```text
generic topology-stream prepared-handle / internal residency / full-M3 phase
accounting work
```

This is not permission to tune a RayJoin app route. The selected target is the
reusable V3 runtime capability exposed by the Spatial/RayJoin workload:
resident query columns, reusable prepared topology-stream handles, complete
phase accounting, and no hot-path host materialization inside RTDL-owned phases.

## Why This Target

M59 removed LibRTS/AABB from the active optimization path. LibRTS is a Set-B
yellow/open control limitation, not a Step-2 Set-A architecture-bearing probe.

The remaining Step-2 question is therefore:

```text
Which Set-A family best tests whether the productized runner generalizes as a
runtime, rather than as another route-specific patch?
```

Spatial/RayJoin is the strongest next selection because it has all four
properties M60 needs:

1. **It is Set-A-shaped.** It is multi-phase topology-stream work, not a
   single-shot control row.
2. **It is currently structural-ready but not material.** M35 explicitly says
   the current runner wraps the same scalar-count executor and removes no new
   physical work.
3. **It has an identified V3 runtime lever.** The M3 gap analysis records a
   device-resident internal route delta: default host-points wall `0.273922s`,
   device-resident points wall `0.120060s`, speedup `2.282x`.
4. **It forces the right engine work.** The missing artifact is not another
   benchmark row; it is a reusable topology-stream prepared handle and a full
   phase table separating static scene prepare, query-stream prepare,
   device-transfer/residency, RT traversal, topology continuation, and host
   return/materialization.

That is precisely the V3 boundary:

```text
RTDL-owned internal device residency between RTDL phases = V3
exposing external host-owned device buffers = V4
```

## Candidate Triage

| Candidate | M60 classification | Why not active target now |
| --- | --- | --- |
| LibRTS/AABB | Set-B yellow/open control limitation | M59 3-AI consensus says it is not the Step-2 runtime optimization gap |
| Barnes-Hut | focused-fix-covered for planning, pending full-suite validation | M45 says the severe frozen regression was already diagnosed and patched through a generic prepared-query surface |
| Grouped reduction | bounded Step-2 technical closure | M43/M44 already moved it from blocked to locally closed for bounded technical purposes, and M53 later backfilled the open Claude review debt; further work risks shape chasing unless tied to a later scorecard need |
| RTDBSCAN/component union | positive component-union evidence, component-signature not material | M40 already supplies the strongest current positive Step-1/Step-2 evidence; M35 says wrapper micro-tuning should stop |
| Spatial/RayJoin topology stream | **selected** | It is the clearest remaining Set-A structural-ready/not-material family with a reusable residency and phase-accounting gap |
| RTNN/Triangle/Hausdorff | scoped positive candidates | Useful later, but M60 prioritizes the family with the clearest unresolved topology-stream runtime lever and blocker history |

## Allowed Next Work

If external review accepts M60, the next goal should be a no-POD local M61
topology-stream runtime packet:

1. Read the current `run_point_location_topology_stream_prepared_session`
   surface and existing Spatial/RayJoin runner payloads.
2. Produce a machine-readable gap ledger for the missing M3 fields and the
   prepared-handle/residency contract.
3. Define the reusable topology-stream prepared handle contract without
   RayJoin-specific native shortcuts.
4. Add or tighten local gates that fail closed if the work becomes route tuning
   or a public performance claim.
5. Defer any focused POD execution until a later reviewed packet names the
   exact command, token, source signature, and stop rules.

M61 may cite grouped-reduction only through the completed M53 debt-backfill
trail, not through the stale M44 sentence that originally recorded Claude debt
as open.

## Forbidden Shortcuts

- Do not tune Spatial/RayJoin app code as the target.
- Do not promote Spatial/RayJoin public wording.
- Do not claim RTDL beats RayJoin from old same-stream evidence.
- Do not call internal device-resident query columns "true zero-copy."
- Do not run M50 or any topology-stream POD command.
- Do not reclassify Set-A/Set-B after seeing results.
- Do not bypass the productized prepared-execution runner to make one row look
  fast.

## Non-Authorization

This report does not authorize:

- no V3 release
- no all-app benchmark run
- no paid POD spend
- no focused POD spend
- no public speedup wording
- no broad V3-over-V2 claim
- no whole-app speedup claim
- no paper reproduction claim
- no V4 work
- no embedding
- no C ABI
- no true-zero-copy claim
- no watch-row closure

## Goal-Level Decision Audit

Decision: select Spatial/RayJoin topology stream as the next Step-2 Set-A
runtime-family target, bounded to generic topology-stream prepared-handle,
internal residency, and full-M3 phase accounting work.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish action would be
   reading "Spatial/RayJoin" as permission for app-specific route tuning or POD.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Select another easy positive probe, but that risks collecting pleasant
   local wins while the structural-ready/not-material topology-stream gap
   remains unsolved.
4. Can I now try a different path that actually solves the problem? Yes. Treat
   Spatial/RayJoin as the probe for a reusable V3 topology-stream runtime
   capability, with no POD and no public claims until separate review.
