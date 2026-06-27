# Goal4168: Current Route Decision After Policy-Aware RT-DBSCAN

Status: accepted current-route registry refresh; no release authorization.

## Purpose

Goals4158-4167 changed the RT-DBSCAN route story:

- all-predicate predicate direct-status has a proven fast path;
- Goal4164 exposes that path as an explicit all-predicate-only mode that fails
  closed on mixed predicate rows;
- Goal4165 shows mixed predicate component-size differences are not explained by
  one grouped-stream configuration switch;
- Goal4166 adds a policy-aware semantic signature;
- Goal4167 updates the app advisor so policy-aware counts-only semantics do not
  imply broad mixed-predicate performance promotion.

Goal4168 refreshes the central current-route registry to match that state.

## What Changed

- `CURRENT_BENCHMARK_ROUTE_DECISION_VERSION` is now
  `rtdl.v2_10.current_benchmark_route_decisions.goal4168.v1`.
- The RT-DBSCAN route row now names the all-predicate-only mode.
- The row now names the policy-aware semantic signature.
- The row explicitly says mixed predicate direct-status remains unpromoted.
- The row rejects hidden border-policy selection in the same way it rejects
  hidden partner, route, and factor selection.

## Boundary

No automatic route, partner, factor, or border-policy selection is authorized.

The registry remains advisory guidance only. It does not authorize release
action, public speedup wording, broad RT-core wording, whole-app acceleration
wording, or app-specific native-engine logic.

## Validation

`tests.goal4168_current_route_decision_after_policy_aware_rtdbscan_test`
