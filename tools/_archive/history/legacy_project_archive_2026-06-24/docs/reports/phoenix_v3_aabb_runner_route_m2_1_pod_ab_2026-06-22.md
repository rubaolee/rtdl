# Phoenix V3 AABB Runner Route M2.1 POD A/B

Date: 2026-06-22
Status: `m2_1_aabb_runner_route_pod_ab_pending_2ai_not_m7`

## Summary

This is focused Phoenix V3 evidence for the generic
`aabb_index_query_2d_native_query_handle` Set-A route after M2.1 route wiring.
The Contact Manifold app is only the harness; the measured route is generic
AABB candidate streaming through `prepared_execution_session_runner`.

Evidence directory:

`docs/rebuild/v3/evidence/phoenix_v3_aabb_runner_m2_1_pod_ab_20260622_180241`

Remote source:

`/root/rtdl_v3_rebuild_20260620/phoenix_v3_aabb_runner_m2_1_pod_ab_20260622_180241`

Hardware:

`NVIDIA RTX 4000 Ada Generation`, driver `550.127.05`, compute capability
`8.9`.

## Protocol

```text
dataset: jittered_grid
grid_count: 32768
indexed_aabb_count: 32768
query_aabb_count: 32768
warmup: 3
repeat: 50
backends: embree,optix
require_rt_hardware: true
```

Both Embree and OptiX payloads report:

```text
productized_execution_path: prepared_execution_session_runner
runtime_executed_count: 50
cache_hit_count: 49
matches_cpu_reference: true
complete_candidate_coverage: true
```

## Result

```text
status: aabb_prepare_reuse_pod_evidence_pending_2ai_not_m7
runner_completed: true
failed_checks: []
productized_runner_visible_for_prepared_backends: true
material_optix_wall_win_after_prepare_reuse: true
m7_reopen_candidate_pending_2ai_review: true
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

Key comparisons:

```text
OptiX / Embree prepare speedup: 0.700x
OptiX / Embree query median speedup: 1.921x
OptiX / Embree query total speedup: 1.738x
OptiX / Embree broadphase wall speedup: 1.348x
OptiX / Embree cold-plus-collect wall speedup: 1.346x
OptiX / Embree runner wall speedup: 1.337x
```

Phase rows:

```text
Embree prepare: 0.423815832 sec
Embree query total: 15.479086533 sec
Embree cold-plus-collect wall: 23.404921278 sec

OptiX prepare: 0.605639882 sec
OptiX query total: 8.906914480 sec
OptiX cold-plus-collect wall: 17.389046729 sec
```

Interpretation: the runner-backed AABB route clears the 1.20x material
cold-plus-collect floor on the RTX 4000 Ada pod. OptiX prepare is still slower
than Embree, so the acceptable claim shape is the measured repeated
prepared-session route, not "OptiX prepare is faster."

## Boundary

This report does not authorize:

- V3 release;
- public speedup wording;
- broad V3-over-V2 wording;
- whole Contact Manifold solver speedup;
- broad AABB index acceleration;
- a full all-app rerun by itself;
- M7 promotion before external review and Codex consensus.

The result is a Set-A focused performance candidate for the productized runner
path. It should be sent through the bounded external-review protocol before any
M7 row reclassification.

## Goal-Level Decision Audit

Decision: record the runner-backed AABB pod A/B as focused Set-A evidence,
not as a release or public claim.

1. Was I foolish?
   No for this decision.
2. If yes, what actions made the decision foolish?
   The foolish action would have been reusing the older 2026-06-21 AABB pod
   rows as if they proved the new runner-backed route, or quoting only hot
   query speedup while hiding prepare and collect costs.
3. Was there another path?
   Yes. I could have skipped the rerun and relied on local route tests plus
   old evidence, but that would leave the productized execution path unproven
   on RT hardware.
4. Can I now try a different path?
   Yes. Keep release blocked, prepare a bounded external-review packet for
   this AABB Set-A candidate, and only consider all-app rerun planning after
   at least two Set-A probes have material focused evidence.
