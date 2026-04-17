## Goal 91: Test Expansion For RayJoin Reproduction

### Objective

Expand the current test surface so the project has stronger unit, system, and
performance confidence for reproducing RayJoin-style experiments on the accepted
backend/workload families.

### Scope

Required test classes:

- unit tests
  - backend-specific correctness helpers
  - dataset normalization / packing / cache behavior
- system tests
  - accepted long exact-source county/zipcode positive-hit `pip` surfaces
  - backend parity and runtime contract checks
- performance tests / harnesses
  - stable measurement paths for the accepted RayJoin-style rows
  - explicit timing-boundary separation

### Required Outcome

- new or strengthened automated tests in `tests/`
- supporting measurement harnesses in `scripts/`
- Linux-backed validation where hardware is required
- published report describing what is now covered and what remains explicitly
  out of scope

### Non-Goals

- no fake claim that every RayJoin experiment is already fully reproduced
- no mixing of correctness and performance boundaries
