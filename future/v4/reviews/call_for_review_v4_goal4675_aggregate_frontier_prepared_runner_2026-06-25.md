# Call For Review: V4 Goal4675 Aggregate-Frontier Prepared Runner

Date: 2026-06-25

Requested verdict labels:

- `accept_goal4675_local_runner_continue_goal4676_protocol`
- `accept_with_required_amendments`
- `reject_goal4675_runner_or_claim_boundary`

## Files To Review

- `future/v4/v4_goal4675_aggregate_frontier_prepared_runner_2026-06-25.md`
- `future/v4/evidence/v4_goal4675_aggregate_frontier_prepared_runner_2026-06-25.json`
- `src/rtdsl/v4_aggregate_frontier.py`
- `src/rtdsl/v4.py`
- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4_scope.py`
- `future/v4/README.md`
- `future/v4/v4_0_scope_gate.md`
- `tests/v4_goal4675_aggregate_frontier_prepared_runner_test.py`
- `tests/v4_frontdoor_test.py`
- `tests/v4_operator_catalog_test.py`
- `tests/v4_scope_gate_test.py`

## Review Questions

1. Does Goal4675 correctly productize
   `v4_aggregate_frontier_device_columns_2d_prepared_runner` as a generic V4
   candidate surface rather than an app-specific Barnes-Hut or force-law
   surface?
2. Does the runner preserve the Goal4674 hot-path boundary: no host frontier row
   materialization before downstream continuation?
3. Does the metadata expose enough phase/residency accounting for Goal4676 to
   make an honest same-hardware performance decision?
4. Does the V4 catalog/frontdoor/scope gate correctly mark this as candidate,
   not measured, not release-authorized, and not public-speed-authorized?
5. Do the tests cover the local contract without pretending to be POD evidence?
6. Is Goal4676 the correct next step, and should it remain the first point where
   same-hardware V2.14/V4 speed claims can be evaluated?
7. Does this review preserve all non-authorization boundaries?

## Expected Non-Authorization

Even if accepted, this review must not authorize V4 release, public speedup
wording, whole-app high-performance wording, POD spend outside Goal4676
protocol, RT-core speedup wording, true-zero-copy wording, Tier-3 callback/PTX
support, raw OptiX callbacks, C ABI, embedding, non-Python hosts, arbitrary
callback claims, automatic partner selection, or app-identity native kernels.
