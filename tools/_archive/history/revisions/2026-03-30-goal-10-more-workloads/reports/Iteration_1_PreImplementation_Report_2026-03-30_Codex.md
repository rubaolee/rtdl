# Iteration 1 Pre-Implementation Report

Date: 2026-03-30
Author: Codex
Round: Goal 10 More Workloads

## Context

Goal 9 completed the Embree evaluation/report baseline. The next practical step
is to expand workload coverage while staying entirely in the local CPU+Embree
phase.

## Proposed Goal 10

Add at least two new executable workload families beyond:

- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`

The initial candidate shortlist is:

- `segment_polygon_hitcount`
- `polygon_polygon_overlap`
- `point_nearest_segment`

## Desired Outcome

For whichever two workloads are selected, Goal 10 should add:

- RTDL source-level support,
- CPU reference semantics,
- Embree execution,
- tests,
- docs/examples,
- and enough dataset support to keep them real rather than purely synthetic.

## Questions For Gemini

1. Is this the right scope for the next Embree-only expansion?
2. Which candidate workloads are the best next choices?
3. What implementation evidence should be required before Goal 10 can be
   accepted complete?
