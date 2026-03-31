# Goal 10 More-Workloads Plan

## Goal

Goal 10 expands the Embree baseline from the original four-workload core to a larger
RTDL workload surface without touching the NVIDIA/OptiX path.

This is still pre-GPU work. The backend remains:

- CPU reference for correctness,
- Embree for real execution,
- and the existing OptiX path only as a compiler/codegen planning target.

## Working Outcome

Goal 10 should deliver:

- at least two additional executable workload families beyond the current four,
- CPU reference semantics for those workloads,
- Embree runtime support for those workloads,
- dataset loaders or deterministic derived datasets for those workloads,
- language docs and example programs,
- and updated evaluation-matrix support where practical.

## Current Baseline

RTDL originally supported:

- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`

Goal 10 starts only after Goal 9, which means:

- the Embree baseline is already frozen and runnable,
- evaluation/report generation already exists,
- and new workloads should be added as additive expansions rather than redesigns.

## Candidate Workload Principles

The next workloads should be chosen to maximize:

- reuse of existing geometry/runtime contracts,
- feasibility on the current Embree architecture,
- usefulness for RayJoin-style or closely adjacent spatial-query programming,
- and teachability in the RTDL language.

## Candidate Families

The initial candidate shortlist is:

1. `segment_polygon_hitcount`
   - Input: segments + polygons
   - Output: one record per segment with polygon hit count
   - Why: reuses current segment and polygon representations while extending
     RTDL toward mixed-geometry queries.

2. `polygon_polygon_overlap`
   - Input: left polygons + right polygons
   - Output: overlap pairs or boolean overlap seeds
   - Why: this deepens the current overlay path into a more explicit direct
     polygon-polygon query workload.

3. `point_nearest_segment`
   - Input: points + segments
   - Output: nearest segment id and distance per point
   - Why: useful as a general RTDL workload even if it is less directly tied to
     the current RayJoin examples.

The implementation phase does not need to include all three. The minimum Goal 10
bar is two new workload families.

## Recommended Selection Criteria

The first two workloads chosen should satisfy:

- one mixed-geometry intersection-style query,
- one polygon- or distance-oriented query,
- shared dataset derivation from existing fixtures where possible,
- and no requirement for exact arithmetic or GPU-only machinery.

## Required Deliverables

Goal 10 implementation should produce:

1. frozen workload contracts for the selected new workloads,
2. Python DSL support,
3. IR and lowering support,
4. CPU reference execution,
5. Embree execution,
6. tests with CPU-vs-Embree parity,
7. example programs,
8. documentation updates,
9. and evaluation-matrix integration or a documented rationale if evaluation
   integration is deferred.

## Acceptance Criteria

Goal 10 is complete when:

- at least two new workload families run through both CPU and Embree,
- those workloads have dataset coverage and examples,
- parity tests pass,
- docs are updated for human and LLM authoring,
- and the review round agrees the added workloads materially expand the Embree
  baseline rather than just reshaping existing cases.

## Non-Goals

Goal 10 does not include:

- NVIDIA/OptiX runtime integration,
- RT-core benchmarking,
- exact or robust arithmetic,
- or major redesign of the Goal 8/Goal 9 Embree baseline.
