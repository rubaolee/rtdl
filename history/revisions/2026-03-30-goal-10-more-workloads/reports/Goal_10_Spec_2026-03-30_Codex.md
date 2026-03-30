# Goal 10 Spec

Date: 2026-03-30
Author: Codex
Round: Goal 10 More Workloads

## Goal

Expand RTDL's Embree baseline to include at least two additional executable
workload families beyond the current four, without entering the NVIDIA phase.

## Current Baseline

The current Embree baseline already covers:

- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`

Goal 10 should add new workload families on top of that baseline.

## Proposed Candidate Shortlist

- `segment_polygon_hitcount`
- `polygon_polygon_overlap`
- `point_nearest_segment`

The minimum acceptable implementation scope is two new workload families.

## Required Outcome

- DSL support
- IR/lowering support
- CPU semantics
- Embree execution
- parity tests
- docs/examples
- dataset path

## Requested Review

Please review this Goal 10 setup and answer:

1. Is the scope technically sound for the current Embree-only phase?
2. Which candidate workloads are the strongest choices?
3. What review criteria should be used later to judge Goal 10 complete?
4. End with a clear decision: either `consensus to begin execution` or `not ready to begin execution`.
