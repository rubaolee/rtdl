# Iteration 1 Pre-Implementation Report

Date: 2026-03-30
Author: Codex
Round: Goal 9 Embree Baseline Reproduction

## Context

Goal 8 completed the Embree baseline as a real local execution foundation:

- frozen workload and ABI contracts,
- CPU and Embree parity on representative cases,
- representative baseline runners,
- a warmup-aware benchmark harness,
- and baseline summary reporting.

The next step is to scale from "baseline exists" to "evaluation can be reproduced
and presented."

## Proposed Goal 9

Use the Embree baseline engine to reproduce as much of the RayJoin evaluation
structure as practical on this Mac, and automatically generate benchmark tables
and figures.

## Proposed Deliverables

- `docs/embree_evaluation_plan.md` as the frozen evaluation plan.
- An evaluation matrix encoded in code and docs.
- Expanded dataset coverage where practical.
- Benchmark artifacts with enough metadata for reporting.
- Table-generation scripts.
- Figure-generation scripts.
- A written evaluation note describing reproduction status and limitations.

## Questions For Gemini

1. Is this the right scope boundary for Goal 9?
2. How should the implementation be reviewed later?
3. Which outputs are mandatory before we can claim consensus completion?
