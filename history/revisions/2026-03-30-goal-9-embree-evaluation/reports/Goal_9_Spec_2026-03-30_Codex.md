# Goal 9 Spec

Date: 2026-03-30
Author: Codex
Round: Goal 9 Embree Baseline Reproduction

## Goal

Reproduce as much of the RayJoin evaluation structure as practical on the RTDL
Embree baseline engine, then generate result tables and figures from the RTDL
benchmark pipeline.

## Scope

- Backend: Embree only for timing results.
- Reference runtime: CPU only for correctness validation.
- Precision mode: `float_approx`.
- Workloads:
  - `lsi`
  - `pip`
  - `overlay`
  - `ray_tri_hitcount`

## Required Outputs

- A frozen evaluation matrix.
- Reproducible benchmark JSON artifacts.
- Generated result tables.
- Generated figure files.
- A written gap analysis versus the RayJoin paper evaluation.

## Working Assumptions

- The current Embree baseline contracts remain the authoritative execution
  contract.
- Public RayJoin-aligned fixtures and derived subsets are acceptable for local
  reproduction.
- The goal is paper-structured local evaluation, not final RT-core parity.

## Risks

- Dataset breadth may exceed what is convenient to keep in-repo.
- Some paper figures may not map cleanly to the current four-workload baseline.
- Figure quality will depend on how much larger-dataset support we can add
  before the GPU phase.

## Requested Review

Please review this goal setup and answer:

1. Is the Goal 9 scope technically sound for the current RTDL baseline?
2. What review criteria should be used later for the implementation phase?
3. Which deliverables are mandatory versus optional for claiming Goal 9 is
   complete?
