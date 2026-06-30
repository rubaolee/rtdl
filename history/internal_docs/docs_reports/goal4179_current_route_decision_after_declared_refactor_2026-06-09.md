# Goal4179: Current Route Decision After Declared RTDBSCAN Refactor

Status: accepted registry consistency refresh; no route promotion.

## Purpose

Goal4176 changed the implementation shape of the caller-declared all-predicate
RT-DBSCAN route. The route no longer feeds synthetic all-true predicate and
neighbor-count columns into the predicate direct-status wrapper. It now calls the
generic all-items direct-status component-signature primitive directly and wraps
that component signature into the RT-DBSCAN app signature at the app boundary.

Goal4177 adds the large-scale pod timing harness for this post-refactor route,
but the pod timing has not run yet because the current pod endpoint refused SSH.

Goal4179 updates the current route-decision registry so readers see the correct
implementation contract without mistaking Goal4176 for fresh timing evidence.

## Registry Decision

The RT-DBSCAN route remains mixed-explicit:

- grouped-stream Numba remains the conservative route for mixed-predicate rows;
- measured all-true predicate direct-status remains explicit and fail-closed;
- caller-declared all-predicate direct-status is explicit and requires external
  proof that all predicate flags are true;
- the declared route now uses the generic all-items direct-status
  component-signature primitive, not synthetic predicate columns;
- Goal4173 timing remains the bounded timing evidence until Goal4177 pod timing
  runs on the post-refactor implementation;
- mixed-predicate direct-status broad promotion remains blocked by Goal4165 and
  Goal4166 policy evidence.

The registry version is now:

`rtdl.v2_10.current_benchmark_route_decisions.goal4179.v1`

## Major Performance Direction

The next real performance/runtime work is not more app tuning. It is one of:

1. Run Goal4177 pod timing to verify the cleaner generic all-items route keeps
   the 2M RT-DBSCAN performance gain.
2. If mixed-predicate rows must beat grouped stream while preserving
   component-size semantics, design a generic border-assignment policy primitive
   rather than hiding a DBSCAN-specific rule in the app.
3. Keep mixed rows on grouped-stream Numba when the user chooses counts-only
   semantics or when no reviewed policy primitive exists.

## External Review Intake

Claude Goal4178 reviewed Goal4176/4177 with verdict `accept-with-boundary` and
found two fixable issues before pod timing should be accepted:

- the declared route's outer metadata still used the old threshold-capped
  neighbor-count policy even though no counts are materialized;
- the Goal4177 runner warmed only the declared route, which could unfairly
  charge first-use Numba work to the grouped-stream baseline.

Both issues are fixed in this Goal4179 slice. The declared route now reports
`not_materialized_all_items_declared_predicate_true` at the outer metadata layer,
and the Goal4177 runner performs a small-input warmup for each measured route
before the large 2M measurement.

## Boundary

This registry refresh does not authorize release, public speedup wording, broad
RT-core wording, whole-app claims, paper-reproduction claims, automatic partner
selection, automatic route selection, automatic factor selection, hidden
border-policy selection, AMD performance claims, app-specific native-engine
logic, or true-zero-copy claims.
