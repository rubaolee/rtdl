# Goal4893: Route A Candidate-Range / Index Redesign Measurement Gate

Date: 2026-07-03

## Goal

Determine whether RTDL can close the RayJoin Section 5.7 directed point-location
candidate explosion through **generic candidate-range / spatial-index
construction changes** before moving to larger data-flow pushdown work.

This goal is a measurement and design gate. It is not a public release goal.

## Decision

After Goal4892, choose **Route A first**.

Reason:

- Goal4890 proved the hot gap is candidate work, not Python/output/writer time.
- Goal4892 proved a cheap in-loop lower-bound prune is correct but not useful:
  vertex PIP map0 moved only `1.079x`, far below the `10x` hard gate.
- The next closest lever is the structure that creates candidate ranges before
  traversal. If that structure is too coarse, no tiny shader-local skip can
  recover the lost work.

Route C, data-flow pushdown/fusion, remains the larger long-term path. It should
not be started until Route A has been falsified or bounded.

## Hypothesis

RTDL's current directed point-location route sends far too many segments into
each OptiX custom primitive because its range construction is too coarse or
poorly aligned with directed point-location queries.

Current RTDL code path:

- `PreparedRayjoinCdbPointLocation2D`
- `GpuRayjoinCdbSegmentRange`
- group modes selected by:
  - `RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE`
  - `RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_SIZE`
  - `RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_AREA_ENLARGE`
  - `RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_ITER`
- known modes:
  - `fixed8`
  - `adaptive`
  - `block_merge64`

AuthorPatch code path:

- `PIPRT`
- `FillPrimitives`
- `FillPrimitivesGroup`
- `FillPrimitivesGroupNew`
- `RTEngine::BuildAccelCustom`

Goal4893 asks whether RTDL's grouping can be changed, generically, to move
toward the author candidate-count denominator without changing the point-location
contract.

## Non-Negotiable Boundaries

Allowed:

- POD scratch instrumentation only;
- reading RTDL and AuthorPatch grouping/index code;
- measuring existing RTDL group modes and parameters;
- proposing a generic planar-map directed point-location indexing design;
- implementing a small scratch-only prototype if the code map identifies a
  plausible generic lever.

Forbidden:

- no public API/docs/tutorial changes;
- no retained product/native code before measurement passes;
- no RayJoin overlay hidden kernel;
- no semantic/comparator change;
- no raw public OptiX callback API;
- no performance claim;
- no V3/V4 revival.

## Measurement Inputs

Primary dataset:

- Australia current-source representative Section 5.7 pair
- left: `/workspace/goal4848_rep/current_osm_au/lakes_Australia_current_osm_Point.cdb`
- right: `/workspace/goal4848_rep/current_osm_au/parks_Australia_current_osm_Point.cdb`
- comparator:
  `/workspace/goal4875_section57_au_representative/author_contract_full/author_contract_au_overlay.txt`

Primary denominator from Goal4890:

| Stage | RTDL baseline | AuthorPatch | RTDL / AuthorPatch |
| --- | ---: | ---: | ---: |
| vertex PIP map0 | 511,943,147,571 | 84,341,083 | 6,069.9x |
| vertex PIP map1 | 36,359,368,176 | 18,561,490 | 1,958.9x |
| midpoint PIP map0 | 68,493,462 | 74,815 | 915.5x |
| midpoint PIP map1 | 105,145,275 | 108,540 | 968.7x |

## Work Plan

### A. Code Map

Map, line-by-line:

1. RTDL range construction in `src/native/optix/rtdl_optix_workloads.cpp`.
2. RTDL traversal loop in `src/native/optix/rtdl_optix_core.cpp`.
3. AuthorPatch `FillPrimitives`, `FillPrimitivesGroup`, and
   `FillPrimitivesGroupNew`.
4. The relationship between author `win`, `enlarge`, `ag_iter`, and RTDL
   `group_mode`, `max_size`, `area_enlarge`, `max_iter`.

Exit requirement:

- state whether existing RTDL modes already represent the author grouping idea
  or whether a missing structural piece remains.

### B. Existing-Mode Measurement Matrix

Run the instrumented RTDL scratch tree across existing generic group modes:

| Mode | Parameters |
| --- | --- |
| fixed8 | default |
| adaptive | max_size `8, 16, 32, 64`, enlarge `1.5, 2.0, 3.5` |
| block_merge64 | max_iter `0, 1, 2, 5`, enlarge `1.5, 2.0, 3.5` |

Each run must report:

- byte equality;
- range count;
- candidate segment-loop counts for the four PIP stages;
- traversal time;
- whether it reaches the hard `10x` candidate reduction gate.

### C. Branch

If an existing mode reaches at least `10x` reduction while preserving byte
equality:

- document the mode as the immediate Route-A candidate;
- propose the minimal productization path;
- do not make a public speed claim yet.

If no existing mode reaches `10x`:

- inspect which structural difference remains against AuthorPatch;
- choose one of:
  - a scratch-only generic range-construction prototype;
  - or close Route A as insufficient and escalate to Route C.

### D. Review

Write:

- measurement result report;
- call-for-review;
- Antigravity review if available;
- Claude review debt if Claude is not available.

## Pass/Fail Gates

Hard pass:

- byte equality true;
- vertex PIP map0 candidate count reduced by at least `10x` vs RTDL baseline;
- no RayJoin-specific public API or hidden overlay kernel;
- route is generic directed point-location / planar-map range construction.

Strong pass:

- vertex PIP map0 candidate count reduced by at least `100x`;
- at least one second directed point-location synthetic workload also benefits.

Fail:

- correctness breaks;
- candidate reduction is below `10x`;
- win comes only from a RayJoin-specific shortcut;
- result requires a semantic/comparator change.

## Expected Result

The most likely useful outcome is not a final optimization but a clear split:

1. either one existing grouping mode was underused and can become the next
   productization candidate;
2. or RTDL is missing the author's real grouping/index structure, and Route A
   needs a deeper generic redesign;
3. or Route A cannot plausibly close the gap, forcing Route C.

## Goal-Level Decision Audit

1. **Am I being stupid?**

   It would be stupid to present Route A / Route C as a choice for the user
   after Goal4890 and Goal4892 already identify the next closest lever. This
   goal chooses Route A first.

2. **What actions would make this decision stupid?**

   Implementing a product change before measuring existing modes, or claiming
   progress because a mode changes wall time without moving candidate counts.

3. **Is there another possible path?**

   Yes, Route C. It is larger and should be entered only after Route A is
   measured or falsified.

4. **Can we start a different path that truly solves the problem?**

   Yes. If Route A fails the frozen gate, start Route C with this evidence
   rather than continuing local grouping tweaks.
