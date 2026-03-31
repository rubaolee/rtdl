# Goal 13: RayJoin Paper Reproduction on Embree

Goal 13 aims to reproduce as much of the RayJoin paper evaluation as possible on top of the current RTDL + Embree baseline.

This is still a pre-NVIDIA phase.

Current status:

- Goal 13 remains active overall, but it is temporarily suspended while Goal 14 evaluates exact-scale readiness for Section 5.6 on the current Mac.
- Completed Goal 13 slices remain valid, especially the accepted Figure 13 / Figure 14 Embree analogue work.

## Purpose

The purpose of Goal 13 is to make RTDL capable of:

- re-running the RayJoin paper workload families now supported by RTDL,
- using RayJoin-aligned datasets and deterministic derived cases,
- benchmarking those workloads on the Embree backend,
- and generating paper-structured tables and figures.

## Why This Goal Matters

This goal creates the strongest pre-GPU validation we can reasonably obtain.

If RTDL can reproduce the paper's evaluation structure on Embree:

- the DSL is closer to the RayJoin problem statement,
- the data pipeline is closer to the final benchmark campaign,
- and the OptiX/NVIDIA phase can focus on backend execution instead of rebuilding the evaluation methodology.

## In-Scope Workloads

- `lsi`
- `pip`
- `overlay`

## Initial Paper Targets

- Table 3 analogue for `lsi` and `pip`
- Table 4 analogue for `overlay`
- Figure 13 analogue for `lsi` scalability
- Figure 14 analogue for `pip` scalability
- Figure 15 analogue for `overlay` speedup summary

Current progress:

- Figure 13 and Figure 14 are now implemented as scaled synthetic Embree analogues.
- Table 3, Table 4, and Figure 15 remain open.

## Main Deliverables

- frozen reproduction checklist
- frozen reproduction matrix
- expanded dataset coverage
- new benchmark cases for paper-target workloads
- generated tables
- generated figures
- generated reproduction report
- gap-analysis note describing differences from the original paper setup

## Acceptance Criteria

- all Goal 13 paper-target cases are recorded in code and docs
- all new cases pass CPU-vs-Embree parity
- all targeted tables and figures generate automatically
- the report clearly labels substitutions and approximations
- Gemini and Codex agree the reproduction baseline is complete for the Embree phase
