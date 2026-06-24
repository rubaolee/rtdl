# Goal 126 Report: Second v0.2 Workload Family Selection

Date: 2026-04-06
Status: accepted

## Summary

After the closure of `segment_polygon_hitcount`, RTDL v0.2 needs one more real
workload-family step that broadens the system without exploding scope.

This report chooses:

- `segment_polygon_anyhit_rows`

as the next major workload-family target.

## Candidate families considered

### 1. Broader `lsi`

Pros:

- clearly important
- historically connected to the project line

Cons:

- too broad for the next immediate closure goal
- too easy to become another long research-surface effort instead of a clean
  v0.2 feature step

Verdict:

- reject for the next immediate goal

### 2. Distance-threshold / nearest-hit workloads

Pros:

- genuinely different
- user-visible

Cons:

- semantics and tie handling are more delicate
- correctness closure is harder
- not the fastest path to a second strong v0.2 family

Verdict:

- reject for the next immediate goal

### 3. `segment_polygon_anyhit_rows`

Pros:

- reuses the now-strong segment/polygon candidate-reduction machinery
- changes the emitted result shape meaningfully
- moves from per-segment aggregation to row materialization
- naturally supports downstream counts, filters, and audits
- can still be validated strongly against PostGIS

Cons:

- close to the first family, so the documentation must explain why it still
  counts as a second family

Verdict:

- accept as the next major v0.2 workload-family target

## Why it counts as a real second family

`segment_polygon_hitcount` computes:

- one row per segment
- aggregated integer count

`segment_polygon_anyhit_rows` would compute:

- one row per true segment/polygon pair
- no aggregation

That changes:

- the result cardinality
- the runtime shape
- the downstream usage pattern
- the validation surface

So this is not just a renamed variant of hitcount. It is a distinct emitted
workload family built on a shared geometric core.

## Proposed next goal

Recommended next implementation goal:

- close `segment_polygon_anyhit_rows` with:
  - explicit semantics
  - authored / fixture / derived datasets
  - parity against Python oracle
  - parity against PostGIS
  - user-facing example
  - Linux large-row performance report

## Final conclusion

The right next major v0.2 technical goal is not another review-only step.

It is:

- one second closed workload family

and the best immediate target is:

- `segment_polygon_anyhit_rows`
