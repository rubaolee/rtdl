# Goal 127: Second Workload Family Any-Hit Rows Closure

Date: 2026-04-06
Status: accepted locally

## Goal

Close the second v0.2 workload family chosen by Goal 126:

- `segment_polygon_anyhit_rows`

This workload should become a real RTDL surface, not just a selected idea.

## Required outcomes

1. add the predicate and lowering path
2. add Python/oracle/native backend execution support
3. add authored deterministic test coverage
4. add one user-facing runnable example
5. thread the family through the baseline and language validation surface
6. state the current environment boundary honestly

## Final status

Goal 127 closes as:

- local second workload family closure
- strong Python/oracle/Embree code-surface integration
- user-facing example added
- baseline/language surface updated

Current environment boundary:

- local Mac native CPU/Embree execution still inherits the existing `geos_c`
  linker limitation for this machine
- so local closure evidence is strongest on:
  - lowering
  - schema validation
  - Python reference execution
  - authored baseline/runtime tests
