# Goal 114: Segment-Polygon Large-Scale PostGIS Validation

Date: 2026-04-05
Status: accepted

## Goal

Strengthen the `segment_polygon_hitcount` v0.2 feature by validating it at a
meaningfully larger deterministic scale against PostGIS ground truth.

## Why this goal exists

Goal 110 closed `segment_polygon_hitcount` as:

- workload-family closure
- semantic/backend closure

Goal 112 then characterized its performance honestly.

But neither goal gave this family an external database-style correctness check
at a scale beyond the small authored / fixture / x4 derived package.

Goal 114 exists to answer the next honest question:

- does the family still return exact per-segment counts when compared directly
  against PostGIS on a substantially larger deterministic case?

## Scope

Primary workload:

- `segment_polygon_hitcount`

Primary external oracle:

- PostGIS `ST_Intersects`

Primary RTDL backends:

- `cpu`
- `embree`
- `optix`

Out of scope:

- claiming RT-core maturity
- replacing Goal 110 or Goal 112
- general PostGIS coverage for all RTDL workloads

## Acceptance boundary

Goal 114 is accepted only if all of the following become true:

1. one explicit large deterministic dataset exists beyond the Goal 110 `x4`
   case
2. one repeatable PostGIS validation driver exists in the repo
3. `cpu`, `embree`, and `optix` are compared against PostGIS on at least one
   large deterministic case
4. the comparison is exact on emitted:
   - `segment_id`
   - `hit_count`
5. the final report states clearly whether the feature now has:
   - stronger external correctness evidence
   - or a remaining correctness gap

## Important honesty note

Goal 114 is a correctness-strengthening step.

It must not be misreported as:

- proof of a new RT-backed traversal design
- proof that the family left the current `native_loop` boundary

unless that separate architectural work actually happens.
