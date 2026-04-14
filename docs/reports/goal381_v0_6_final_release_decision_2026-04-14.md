# Goal 381 Report: v0.6 final release decision

## Decision

Accept: the current `v0.6` package should move to `v0.6.0` release-making.

## Why

The required release-prep ladder is now closed:

- Goal `377`:
  - total code review and test gate
- Goal `378`:
  - total doc review, update, and verification
- Goal `379`:
  - total goal-flow audit
- Goal `380`:
  - final external release review

The `v0.6` package is now supported by:
- bounded graph workload scope
- Python/oracle correctness line
- PostgreSQL supporting baseline
- bounded Linux synthetic and real-data evidence
- corrected PostgreSQL timing methodology
- saved review and audit material across the release-prep chain

## Honest release boundary

This decision accepts `v0.6.0` as:
- the graph-workload expansion release
- bounded to:
  - `bfs`
  - `triangle_count`
- Linux-primary for real evaluation claims
- Python/oracle/PostgreSQL for the accepted graph runtime/baseline story

This decision does not accept claims of:
- full graph-system closure
- accelerated graph backend closure
- full cross-platform graph maturity
- paper-scale benchmark closure

## What remains after this decision

Only the release-making mechanics remain:
- promote the front door and docs index from release-prep wording to released
  `v0.6.0` wording
- update the `v0.6` release package from "under preparation" to released state
- record the final release-make state
- tag `v0.6.0`
