# Goal 2 Spec

Date: 2026-03-29
Author: Codex
Round: 2026-03-29-goal-2-multi-workload-datasets

## Objective

Extend RTDL beyond the current single narrow segment-join path so that the compiler, IR, and Python data pipeline can cover at least three RayJoin workload surfaces without requiring GPU runtime execution yet.

## Why This Goal Is Next

Goal 1 stabilized the compiler contract for one workload. The next pre-GPU bottleneck is coverage:

- the DSL and IR are still too narrow,
- the repository does not yet ingest RayJoin datasets,
- and there is no CPU-side pipeline for validating multiple workload semantics before OptiX runtime integration.

This goal addresses those gaps while the project is still CPU-only.

## Proposed Workload Scope

Target at least these three workload surfaces:

1. Line Segment Intersection (`lsi`)
2. Point-in-Polygon (`pip`)
3. Polygon overlay preparation/composition as an RTDL-visible workload surface, grounded in LSI + PIP results

The third item may be implemented as an explicit overlay-oriented IR/workflow rather than a full final overlay runtime, but it must materially extend the language and plan model beyond just adding another predicate.

## Proposed Dataset Scope

Use RayJoin-origin data first so the work stays grounded in the actual backend target.

Primary candidate inputs:

- RayJoin sample data under `test/dataset` from the public RayJoin repository
- RayJoin-public polygon datasets such as County/Zipcode or BlockGroup/WaterBodies when practical

The dataset pipeline should be able to:

- fetch or register dataset sources,
- parse the chosen RayJoin-aligned formats,
- normalize them into RTDL-friendly Python structures,
- derive workload-specific probe/build views such as segments, polygons, and point sets when needed.

## Deliverables

1. Python DSL extensions for at least three workload surfaces
2. IR extensions needed to represent them cleanly
3. RayJoin lowering support for those workload surfaces at the plan/codegen-contract level
4. Python dataset loaders/preprocessing for selected RayJoin datasets
5. CPU-side reference or semantic tests for the selected workloads and datasets
6. Documentation of supported workloads and selected dataset pipeline

## Non-Goals

- real OptiX runtime execution
- GPU performance claims
- robust/exact precision parity with RayJoin
- full production overlay implementation if the overlay surface is represented compositionally instead

## Success Criteria

Goal 2 is complete if:

- RTDL can express at least three RayJoin workload surfaces,
- each of those workloads lowers into a backend plan,
- selected RayJoin datasets can be ingested through a Python pipeline,
- tests cover both compiler artifacts and dataset-to-workload transformations,
- and Codex/Gemini agree that the work materially advances v0.1 workload coverage.

## Open Design Questions

1. Which exact three workloads are the best scope for this round?
2. Should overlay count if implemented as composition over LSI + PIP rather than as a standalone final executor?
3. Which RayJoin datasets are the best fit for a CPU-only validation pipeline?
4. What evidence should count as sufficient review consensus before implementation is accepted?
