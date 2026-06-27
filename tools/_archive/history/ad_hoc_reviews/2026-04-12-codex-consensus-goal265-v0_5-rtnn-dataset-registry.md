# Codex Consensus: Goal 265 v0.5 RTNN Dataset Registry

Date: 2026-04-12
Goal: 265
Status: pass

## Judgment

The new RTNN registry is a bounded, technically honest addition.

It cleanly separates:

- dataset families
- experiment targets
- bounded local profiles

and it does so without overclaiming dataset acquisition or paper reproduction.

## Why It Matters

The previous `v0.5` line had real API and correctness progress, but the paper
consistency story still lacked a concrete data-layer source of truth. This goal
fixes that gap in a small and reviewable way.

## Important Boundaries Preserved

- all seeded dataset families are explicitly 3D
- bounded reproduction is kept distinct from exact reproduction candidates
- RTDL extension targets remain labeled as extensions, not paper-faithful runs
- the `v0.5` goal ladder is now aligned with the actual work already landed

## Remaining Work

Goal 266 should now decide the baseline-library harness layer, and Goal 267
should turn the new registry plus baseline decisions into the first labeled
reproduction matrix.
