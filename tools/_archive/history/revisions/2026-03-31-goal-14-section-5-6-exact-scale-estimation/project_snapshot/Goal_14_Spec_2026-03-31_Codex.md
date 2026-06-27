# Goal 14 Spec

Date: `2026-03-31`
Author: `Codex`

## Goal

Estimate whether RTDL can repeat RayJoin Section 5.6 at the original nominal data sizes on the current Mac, and document:

1. predicted runtime,
2. predicted feasibility limits,
3. and what would be required to compare CPU execution against GPU RT-hardware execution later.

## Scope

- exact-scale paper target only:
  - fixed `R = 5,000,000`
  - varying `S = 1,000,000 .. 5,000,000`
- workloads:
  - `lsi`
  - `pip`
- backend focus:
  - current Mac
  - current RTDL implementation
  - current Embree-first local architecture

## Deliverables

- [goal_14_section_5_6_exact_scale_plan.md](/Users/rl2025/rtdl_python_only/docs/goal_14_section_5_6_exact_scale_plan.md)
- [goal_14_section_5_6_exact_scale_estimation_2026-03-31.md](/Users/rl2025/rtdl_python_only/docs/reports/goal_14_section_5_6_exact_scale_estimation_2026-03-31.md)
- a reproducible generator:
  - [generate_goal14_section56_estimation.py](/Users/rl2025/rtdl_python_only/scripts/generate_goal14_section56_estimation.py)

## Acceptance Boundary

Goal 14 is complete if Codex and Gemini agree that:

- the report is technically honest,
- the runtime estimate is grounded in current RTDL measurements,
- the feasibility limit is stated clearly,
- and the CPU-vs-GPU comparison section is methodologically sound.
