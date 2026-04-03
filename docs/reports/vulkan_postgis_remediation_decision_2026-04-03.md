# Vulkan And PostGIS Remediation Decision

Date: 2026-04-03
Status: draft for external review before edits

## Scope

This decision covers two active issues:

1. unexpected Vulkan backend commits that landed on `main` while the project was under other active work
2. the in-progress Goal 50 PostGIS ground-truth comparison on `192.168.1.20`

## Vulkan Decision

### Current decision

Keep the Vulkan backend on `main`, but downgrade its status to provisional until the following issues are fixed and re-reviewed:

- LSI output-capacity truncation in `src/native/rtdl_vulkan.cpp`
- missing guardrails for large `point_count * poly_count` / `left_count * right_count` output allocations
- incomplete committed Vulkan unit coverage
- over-strong acceptance wording in Vulkan review and consensus docs

### Why not revert

- the Vulkan backend is substantial and coherent
- the Python integration shape is consistent with the other backends
- no architectural or static-analysis finding currently justifies discarding the whole backend

### Why not fully accept

- the current test surface is not strong enough to justify the strongest readiness claims
- the current memory contract is unsafe for larger workloads
- the current docs say more than the validation evidence proves

## PostGIS Decision

### Current decision

The previously running PostGIS comparison on `192.168.1.20` is rejected as an accepted run and must not be used for correctness or performance conclusions.

### Reason

The live SQL observed on the host for the old `lsi` run did not use the `geom &&` GiST-index-assisted bbox predicate. It was therefore not an acceptable indexed spatial-database comparison for this project goal.

The stale PostGIS backends have been terminated.

### Ground-truth policy

PostGIS is used here as:

- an industrial-standard spatial database comparison target
- an additional external correctness reference for RTDL

Therefore accepted PostGIS runs must satisfy all of the following:

- indexed query strategy
- semantics aligned with RTDL
- load/index-build time reported separately from query time

### Required query mode

- `lsi`: `l.geom && r.geom` bbox pruning followed by RTDL-matching exact segment math
- `pip`: `g.geom && p.geom` plus `ST_Covers(g.geom, p.geom)` for boundary-inclusive positive-hit rows

## Required next edits

1. Vulkan:
   - fix capacity overflow and add hard guardrails
   - add committed coverage for the two missing workloads
   - downgrade readiness wording in Vulkan docs to provisional status
2. PostGIS:
   - update Goal 50 docs to describe the indexed query mode accurately
   - strengthen tests so the indexed SQL strategy is asserted directly
   - rerun only under the accepted indexed-ground-truth policy

## Acceptance rule for this remediation round

No code or doc changes from this round should be committed until:

- Claude reviews the Vulkan fix scope and proposed edits
- Gemini reviews the report and the remediation result
- Codex reviews both and records the final keep/provisional consensus
