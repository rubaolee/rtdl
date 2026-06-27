# V4 Goal4675 Aggregate-Frontier Prepared Runner

Date: 2026-06-25

Status:

```text
goal4675_local_runner_productization_complete_pod_not_authorized
```

Decision label:

```text
aggregate_frontier_device_columns_v4_candidate_runner_productized__goal4676_focused_pod_protocol_may_be_prepared__pod_not_yet_authorized
```

Machine evidence:

```text
future/v4/evidence/v4_goal4675_aggregate_frontier_prepared_runner_2026-06-25.json
```

## Decision

Goal4675 productizes a local V4 candidate runner for:

```text
AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D
```

through the V4 public front door:

```text
v4_aggregate_frontier_device_columns_2d_prepared_runner
```

This is a candidate surface only. It is not measured on POD, not counted as one
of the 8 measured V4 operator surfaces, and not authorized for release or
performance wording.

## What Changed

Implemented:

- `src/rtdsl/v4_aggregate_frontier.py`
- `prepare_aggregate_frontier_device_columns_2d_prepared_runner_v4`
- `V4AggregateFrontierDeviceColumns2DPreparedRunner`
- `aggregate_frontier_device_columns_2d_prepared_runner_claim_boundary_v4`

Wired into:

- `src/rtdsl/v4.py`
- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4_scope.py`
- `future/v4/README.md`
- `future/v4/v4_0_scope_gate.md`

The runner delegates to the existing generic native prepared route:

```text
prepare_aggregate_frontier_device_columns_2d_optix
PreparedOptixAggregateFrontierDeviceColumns2D.run_device_columns
```

It does not add Barnes-Hut, force-law, DBSCAN, RayJoin, or any other
app-identity native surface.

## Contract

The runner records V4 metadata around the generic aggregate-frontier
device-column primitive:

```text
generic_primitive: AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D
continuation_class: aggregate_frontier_device_columns
backend: optix
downstream_partner: none | cupy | numba
```

It preserves the Goal4674 hot-path rule:

```text
host_materialization_in_hot_path: false
frontier_columns_materialized_on_host: false
row_offsets_materialized_on_host: false
```

If the underlying prepared output reports host frontier or row-offset
materialization, the runner fails closed instead of returning a false
device-resident claim.

Phase accounting is first-class in the runner metadata:

```text
aggregate_frontier_traversal_seconds
downstream_partner_seconds
host_frontier_materialization_seconds
phase_accounting_is_first_class
```

## Front Door Status

The V4 operator catalog now exposes two candidate surfaces:

```text
v4_fixed_radius_ranked_summary_3d_prepared_runner
v4_aggregate_frontier_device_columns_2d_prepared_runner
```

The aggregate-frontier runner is recognized by the V4 pushdown planner as:

```text
pushdown_recognized_candidate_tier2_not_measured
```

It is not a measured release surface.

## Tests

Passed:

```text
py -m unittest tests.v4_goal4675_aggregate_frontier_prepared_runner_test
```

Result:

```text
Ran 7 tests in 0.002s
OK
```

Passed:

```text
py -m unittest tests.v4_frontdoor_test tests.v4_operator_catalog_test tests.v4_scope_gate_test tests.v4_goal4674_aggregate_frontier_device_columns_gate_test
```

Result:

```text
Ran 29 tests in 2.434s
OK
```

Both commands printed the existing local Python warning:

```text
Could not find platform independent libraries <prefix>
```

The unittest results passed.

## Goal4676 Authorization

Goal4675 authorizes preparing Goal4676 focused POD protocol/benchmark work only.
It does not by itself authorize running POD outside that protocol.

Goal4676 must prove, on same RT hardware and same-contract inputs:

- V4 vs the strongest V2.14 aggregate-frontier denominator;
- correctness parity;
- row-offset parity;
- downstream weighted-vector summary parity;
- no host frontier materialization before partner continuation;
- phase accounting that separates aggregate-frontier traversal from downstream
  continuation;
- no counting partner migration as a V4 speed win.

## Review State

- Codex: local implementation and self-audit complete.
- Claude: weekly limit known until 2026-06-28 19:00 America/New_York; review
  debt is recorded instead of probing repeatedly.
- Antigravity: accepted with verdict
  `accept_goal4675_local_runner_continue_goal4676_protocol`.

This satisfies the "continue with review debt allowed" rule for local work only.
It does not authorize release.

## Goal-Level Decision Audit

1. Was I being stupid?
   - No for this goal. The implementation stayed local, candidate-only, and did
     not claim performance.
2. If yes, what action would have made it stupid?
   - Running POD or claiming V4 speed immediately after wrapping the local
     prepared route would have repeated the old mistake.
3. Is there another path that avoids getting stuck on that premise?
   - Yes. Register the runner as candidate-only and force Goal4676 to carry the
     first same-hardware performance proof.
4. Can I now try the different path that actually solves the problem?
   - Yes. Proceed to Goal4676 focused protocol/benchmark gating, with no public
     claim until the measurement passes.

## Non-Authorization

This goal does not authorize V4 release, public speedup wording, whole-app
high-performance wording, POD spend outside Goal4676 protocol, RT-core speedup
wording, true-zero-copy wording, Tier-3 callback support, raw OptiX callbacks,
C ABI, embedding, non-Python hosts, arbitrary callback claims, automatic partner
selection, or any app-identity native kernel.
