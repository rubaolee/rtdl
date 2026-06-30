# Goal4175: Current Route Decision After Declared RT-DBSCAN Evidence

Status: accepted registry refresh; no route promotion.

## Purpose

Goal4173 added reviewed pod evidence for the explicit caller-declared
all-predicate RT-DBSCAN route. Goal4175 updates the current benchmark route
decision registry so a reader sees the new evidence without mistaking it for an
automatic route promotion.

## Decision

The RT-DBSCAN route remains mixed-explicit:

- grouped-stream Numba remains the conservative route for mixed-predicate rows;
- measured all-true predicate direct-status remains explicit and fail-closed;
- declared all-true predicate direct-status is available only when the caller
  externally proves that all predicate flags are true;
- mixed-predicate direct-status broad promotion remains blocked by Goal4165 and
  Goal4166 policy evidence.

The registry version is now:

`rtdl.v2_10.current_benchmark_route_decisions.goal4175.v1`

## Goal4173 Route Evidence Recorded

The registry now records that Goal4173 measured the declared route on the 2M
road3d row with the same RT-DBSCAN signature:

`cluster_sizes = {1: 2097152}, core_count = 2097152, noise_count = 0`

The declared route skips RT count-threshold execution, records no RT-core claim
for the declared-predicate subpath, and improves warmed elapsed timing by:

- `1.662x` versus the current grouped-stream route;
- `1.211x` versus the measured all-true wrapper.

## Boundary

This registry refresh does not authorize release, public speedup wording, broad
RT-core wording, whole-app claims, paper-reproduction claims, automatic partner
selection, automatic route selection, automatic factor selection, hidden
border-policy selection, AMD performance claims, app-specific native-engine
logic, or true-zero-copy claims.
