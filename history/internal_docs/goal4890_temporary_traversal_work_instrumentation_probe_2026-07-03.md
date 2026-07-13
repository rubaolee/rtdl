# Goal4890: Temporary Traversal Work Instrumentation Probe

Date: 2026-07-03

## Purpose

Goal4889 proved that RTDL and AuthorPatch launch the same query counts for the
Australia representative Section 5.7 workload, but the decisive denominator is
still missing:

- how many candidate segment/intersection tests RTDL performs; and
- how many candidate segment/intersection tests AuthorPatch performs.

Goal4890 exists only to measure that denominator. It is not an optimization goal.

## Authorized Work

Use a temporary scratch/POD measurement copy to add counters for:

### RTDL

1. LSI grouped-range direct row route:
   - group-candidate event count;
   - emitted row count;
   - query segment count.
2. Directed planar-map point-location / PIP route:
   - total segment-loop iterations in the point-location intersection program;
   - query point count;
   - positive-face count.

### AuthorPatch

1. LSI RT path:
   - candidate/intersection test count;
   - emitted intersection count;
   - query segment count.
2. PIP RT path:
   - candidate edge/range test count;
   - query point count;
   - positive-face count.

## Forbidden Work

Do not modify the released product line or public surface.

Forbidden in this goal:

- prepared sessions;
- row-buffer ABI;
- Numba partner API implementation;
- native kernel tuning;
- callback APIs;
- data-flow fusion/compiler implementation;
- RayJoin-specific fast paths;
- comparator or geometry semantic changes;
- public docs/tutorial/release wording;
- public performance claims.

Temporary counter-only edits are allowed only inside the measurement scratch copy.

## Required Inputs

Use the same Australia representative Section 5.7 inputs already used for the
bounded RayJoin reproduction:

- lakes Australia current OSM CDB;
- parks Australia current OSM CDB;
- AuthorPatch comparator/build used by the bounded reproduction line;
- RTDL v2.14 product code plus only temporary counter instrumentation.

## Verification Gates

The measurement run must record:

1. RTDL and AuthorPatch query counts still match.
2. RTDL and AuthorPatch output correctness remains unchanged for the measured
   route.
3. Candidate/test counts are recorded for LSI and PIP on both sides.
4. Artifacts include raw logs, command lines, code diff summary, and a
   machine-readable JSON result.

## Decision Labels

Use exactly one:

- `candidate_explosion__dataflow_pushdown_or_in_traversal_pruning_next`
- `same_candidates__native_kernel_path_tuning_next`
- `mixed_lsi_pip__split_work_next`
- `instrumentation_failed__redo_probe`

## Goal-Level Decision Audit

1. **Am I being stupid?**

   It would be stupid to optimize before the candidate/test denominator is
   measured. This goal avoids that by only adding temporary counters.

2. **What would make this goal stupid?**

   Letting temporary instrumentation become product code, or changing semantics
   while measuring.

3. **Is there another path?**

   Not a better one. Existing logs lack the required denominator.

4. **Can we start a different path that truly solves the problem?**

   Only after this probe. The result decides whether the true path is
   data-flow/in-traversal pruning or native kernel tuning.
