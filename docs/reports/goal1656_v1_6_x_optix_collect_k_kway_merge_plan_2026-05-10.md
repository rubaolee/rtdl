# Goal1656 v1.6.x OptiX Collect-K K-Way Merge Plan

## Verdict

`kway_merge_native_probe_prepared`

This is a local planning artifact for the next OptiX `COLLECT_K_BOUNDED`
merge-chain diagnostic. It records topology and correctness expectations only;
it does not contain GPU timing.

## Current Shape

- Candidate count: `262144`.
- CUB tile count: `128`.
- Segment capacity: `2048`.
- Current binary segment chain: `[128, 64, 32, 16, 8, 4, 2, 1]`.
- Current estimated merge-side kernel launches: `27`.

## Candidate Shape

- Four-way segment chain: `[128, 32, 8, 2, 1]`.
- Four-way merge levels: `4`.
- Four-way estimated merge-side kernel launches: `15`.
- Eight-way reference-only chain: `[128, 16, 2, 1]`.

The first native diagnostic should target four-way merge rather than eight-way
merge. Four-way reduces the merge chain substantially while keeping the rank
calculation bounded to three peer searches per input row. Eight-way is kept as
a topology reference only because seven peer searches per row is more likely to
increase register pressure and memory traffic before proving the idea.

## Correctness Contract

The diagnostic must preserve the existing row-width=2 `COLLECT_K_BOUNDED`
contract:

- Input segments are individually sorted.
- Output rows are globally sorted.
- Duplicate rows across any input segment are emitted once.
- Capacity bounds are applied after global sort and dedupe.
- Overflow behavior and emitted-count semantics must match the accepted path.

Reference sample unbounded output:

`[(0, 0), (1, 10), (2, 20), (3, 30), (4, 40), (5, 50), (7, 70), (8, 80), (9, 90)]`

Reference sample capacity-5 output:

`[(0, 0), (1, 10), (2, 20), (3, 30), (4, 40)]`

## Next Native Probe

Add an opt-in diagnostic only, not enabled by
`RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE`, that compares:

- Control: current accepted CUB + binary compact-level merge path.
- Candidate: current CUB sort plus four-way compact-level merge for eligible
  full groups, falling back to the accepted binary/carry handling where needed.

The pod acceptance gate should require parity, same emitted count, same
overflow flag, and a measured total-time win before considering any promotion.

## Claim Boundary

This report does not authorize public speedup wording, stable
`COLLECT_K_BOUNDED` promotion, fastest-candidate promotion, release tags, or
release action.
