# Goal 191: v0.3 Comprehensive Verification

## Objective

Run a comprehensive pre-release verification sweep across the RTDL stack, from the
initial rayjoin-style workloads through the bounded 3D visual demo layer, using
selected small artifacts rather than expensive production renders.

## Why

The repo has accumulated many slices across:

- workload kernels
- backend runtimes
- Python-hosted application logic
- visual-demo proofs

Before a real `v0.3` release, the project needs one deliberate verification pass that
proves the current final repo shape still holds together end to end.

## Scope

- verify the released/core workload surface from the early RTDL line
- verify bounded backend/runtime slices that represent the CPU, Embree, OptiX, and Vulkan paths
- verify the moved `examples/visual_demo/` programs in bounded form
- include small video generation where useful
- allow small local Embree video generation on macOS if needed for bounded verification
- do not depend on long Windows HD rerenders
- write a final verification report with explicit pass/skip/failure accounting

## Required Coverage

- initial workload line:
  - rayjoin / hitcount / overlap / Jaccard style surfaces
- backend/runtime line:
  - oracle / CPU reference
  - Embree
  - OptiX
  - Vulkan
- application/demo line:
  - bounded direct runs of the current visual demo programs
  - at least one small bounded video artifact path

## Non-goals

- no expensive Windows HD movie reruns
- no new feature work
- no visual redesign of the demo line
- no release packaging yet

## Success Criteria

- a bounded but comprehensive verification slice is selected and executed
- failures are either fixed or honestly documented as release blockers
- the verification report clearly states what was run, skipped, and deferred
- the goal closes only under:
  - Codex consensus
  - Claude review
  - Gemini review

## Release Relationship

- This is one of the two final pre-release goals before `v0.3` release packaging.
