# Goal4180: Current Route Decision After Goal4177 RTDBSCAN Timing

Status: accepted registry refresh; no automatic route promotion.

## Purpose

Goal4177 completed the post-refactor 2M pod timing for the caller-declared
all-predicate RT-DBSCAN route. Goal4180 updates the current route-decision
registry so it records Goal4177 as accepted evidence rather than a pending
timing harness.

## Decision

The RT-DBSCAN route remains mixed-explicit:

- grouped-stream Numba remains the conservative route for mixed-predicate rows;
- measured all-true predicate direct-status remains explicit and fail-closed;
- caller-declared all-items direct-status is explicit and requires external
  proof that all predicate flags are true;
- the declared all-items route is the fastest measured all-predicate route on
  the 2M road3d row, with `1.704x` elapsed speedup over current grouped stream
  and `1.269x` over measured all-true predicate direct-status;
- mixed-predicate direct-status broad promotion remains blocked by Goal4165 and
  Goal4166 policy evidence.

The registry version is now:

`rtdl.v2_10.current_benchmark_route_decisions.goal4180.v1`

## Boundary

This registry refresh does not authorize release, public speedup wording, broad
RT-core wording, whole-app claims, paper-reproduction claims, automatic partner
selection, automatic route selection, automatic factor selection, hidden
border-policy selection, mixed-predicate direct-status promotion, AMD
performance claims, app-specific native-engine logic, or true-zero-copy claims.

The next major runtime direction is not more app-specific tuning. It is either
prepare-cost/profile-coverage hardening for the promoted explicit routes, or a
generic border-assignment policy primitive if mixed-predicate component-size
distributions must become contractual and fast.
