# RayJoin Paper Reproduction Checklist

This document defines the practical checklist for reproducing the RayJoin paper evaluation through RTDL on the current Embree baseline.

It is a pre-NVIDIA goal. The purpose is not to match the paper's hardware numbers, but to:

- express the paper's workload surface in RTDL,
- run the workloads through the current local engine,
- use RayJoin-aligned datasets where possible,
- generate corresponding benchmark tables and figures,
- and make the eventual OptiX/NVIDIA phase a backend transition instead of a semantic redesign.

## Goal

Use RTDL plus the current Embree engine to cover as much of the RayJoin paper evaluation surface as possible, then generate the corresponding RTDL tables and figures.

## Paper Scope We Need To Reproduce

Based on the RayJoin paper and project page, the current evaluation surface to target is:

- `LSI` query performance
- `PIP` query performance
- polygon overlay as the composed application built from LSI + PIP
- scalability plots for LSI
- scalability plots for PIP
- overlay speedup summary and execution-time tables

The key paper artifacts to mirror are:

- Table 3: LSI and PIP performance numbers
- Figure 13: LSI scalability
- Figure 14: PIP scalability
- Table 4: polygon overlay execution time
- Figure 15: polygon overlay speedup summary

## RTDL Mapping Status

Current RTDL status:

- `lsi`: implemented
- `pip`: implemented
- `overlay`: implemented as compositional seed generation, not full polygon overlay materialization
- `ray_tri_hitcount`: implemented, but not part of the RayJoin paper reproduction target
- `segment_polygon_hitcount`: implemented, but not part of the RayJoin paper reproduction target
- `point_nearest_segment`: implemented, but not part of the RayJoin paper reproduction target

So the reproduction target should focus first on:

1. `lsi`
2. `pip`
3. `overlay`

## Required Workstreams

### 1. Freeze the paper reproduction matrix

For each paper-target case, define:

- RTDL workload
- dataset name
- dataset provenance
- expected output schema
- backend(s) to run
- whether the case feeds a table, figure, or both

### 2. Expand dataset coverage

For each paper table/figure:

- identify the original RayJoin dataset pair or distribution
- decide whether we can use:
  - checked-in public fixture subset,
  - downloaded RayJoin sample data,
  - deterministic derived enlargement,
  - or deterministic synthetic generators
- document any substitution clearly

### 3. Ensure semantic coverage

For every reproduction case:

- RTDL kernel exists
- CPU reference semantics exist
- Embree execution exists
- parity checks pass

### 4. Build figure-specific generators

Add explicit output generators for:

- Table 3 style summary
- Table 4 style summary
- Figure 13 style LSI scalability plots
- Figure 14 style PIP scalability plots
- Figure 15 style overlay speedup plots

### 5. Track reproduction fidelity

For every figure/table:

- mark as `exact-input`, `derived-input`, or `synthetic-input`
- document what differs from the paper
- document what still must wait for the NVIDIA phase

## Acceptance Criteria

This goal is complete when:

- the RTDL Embree evaluation matrix explicitly includes all current paper-target cases,
- `lsi`, `pip`, and `overlay` cases all pass CPU-vs-Embree parity,
- RTDL generates the corresponding tables and figures,
- the report clearly distinguishes exact reproduction from Embree baseline approximation,
- and the full round is accepted by at least 2-agent consensus.

## Non-Goals For This Phase

- NVIDIA RT-core benchmarking
- OptiX runtime reproduction
- exact match to paper timing values
- robust/exact arithmetic parity with the paper's conservative representation

## Recommended Execution Order

1. Freeze the paper reproduction matrix.
2. Map the paper datasets into RTDL dataset categories.
3. Extend the evaluation matrix for all `lsi`, `pip`, and `overlay` paper cases.
4. Add table-specific and figure-specific generators.
5. Validate parity for every new case.
6. Generate the RTDL Embree reproduction report.
7. Review with Gemini and iterate until consensus.
