# Goal 347 Review: v0.6 PostgreSQL graph-baseline plan

## Decision

Accept.

## Why

- the goal is bounded to baseline selection rather than implementation sprawl
- PostgreSQL is the correct SQL/database baseline for `v0.6` graph workloads
- the saved external review supports the choice as honest and bounded
- the goal sits in the right place in the sequence before the BFS and
  triangle-count PostgreSQL implementation goals

## Important boundary

This goal does not prove implementation quality by itself.

It closes the baseline-selection decision that later Goals `348` and `349`
implement.
