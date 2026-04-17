# Goal 41 Cross-Host Oracle Correctness

Date: 2026-04-02

## Goal

Validate the new native C/C++ oracle across both available hosts:

- this Mac
- `192.168.1.20`

with two rules:

1. small cases: Python oracle, C oracle, and Embree must all match
2. larger cases: C oracle and Embree must match

## Scope

This goal includes:

- a small 3-way correctness sweep on both hosts
- a larger C-oracle-vs-Embree sweep on both hosts
- explicit reporting of any portability issues found during the run

This goal does not include:

- introducing a new benchmark harness into the repository
- adding GPU or OptiX validation
- claiming full paper-scale nationwide closure

## Acceptance

Goal 41 is accepted if:

- small cases match on both hosts across Python oracle, C oracle, and Embree
- larger cases match across C oracle and Embree
- any issues discovered during the sweep are fixed and documented
