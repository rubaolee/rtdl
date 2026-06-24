# Phoenix V3 Fixed-Radius Self-Query Runner Binding M1.1

Date: 2026-06-22
Status: `m1_1_fixed_radius_self_query_runner_binding_validated_not_release`

## Summary

This report records the first real generic primitive binding for the Phoenix V3
prepared execution/session runner after Claude's `approve_blocked_not_release`
review.

Files changed:

- `src/rtdsl/prepared_execution.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`

The new helper:

- routes the generic `fixed_radius_count_threshold_self_query` primitive through
  `run_prepared_execution_session`;
- requires explicit partner choice;
- uses the existing explicit prepared-session cache/residency contract;
- calls the existing adapter
  `fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns`;
- records `runtime_executed: true`;
- marks the row as a Set-A probe candidate;
- keeps release/public/broad/true-zero-copy/automatic-selection claims false.

This is a contract and execution-path binding, not a pod performance result.

Follow-up route wiring:

```text
docs/reports/phoenix_v3_grouped_stream_runner_route_m1_2_2026-06-22.md
status: m1_2_runner_backed_fixed_radius_probe_route_validated_not_release
```

## What Changed

`src/rtdsl/prepared_execution.py` now exposes:

```text
run_fixed_radius_count_threshold_3d_self_query_prepared_session
```

The helper is deliberately generic. It does not know RTDBSCAN, Hausdorff,
Barnes-Hut, or any benchmark app. It binds a reusable primitive family that
those apps can probe later.

The helper accepts caller-owned `search_points`, `radius`, `threshold`,
explicit `partner`, explicit cache, optional output columns, optional prepare
function, and optional validation function. It prepares or reuses a native
OptiX fixed-radius self-query handle, then executes the existing partner-device
adapter through the new runner.

## Validation

Focused runner and fixed-radius contract tests:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.goal4486_rt_dbscan_self_count_threshold_test \
  tests.v3_phoenix_fixed_radius_graph_self_query_refresh_test

13 tests OK
```

Prepared execution compile gate:

```text
PYTHONPATH=src;. py -3 -m py_compile src/rtdsl/prepared_execution.py
OK
```

Release/protocol/selection gates:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_external_verdict_intake_test \
  tests.v3_phoenix_next_dominant_hotpath_selection_test \
  tests.v3_phoenix_major_performance_mandate_gate_test \
  tests.v3_phoenix_release_readiness_gate_test \
  tests.v3_release_wording_gate_test

24 tests OK
```

Legacy prepared-session/fixed-radius compatibility gates:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal756_prepared_db_app_session_test \
  tests.goal757_prepared_optix_fixed_radius_count_test

20 tests OK, 2 skipped
```

## Non-Claims

This packet does not claim:

- V3 is release-ready.
- V3 broadly beats V2.x.
- The fixed-radius runner binding improves performance yet.
- The binding is already used by a benchmark route.
- Another full all-app pod run is authorized.
- True zero-copy is implemented or authorized.
- V4/C ABI/embedding scope belongs in Phoenix V3.

## Next Work

M1.2 must make the runner observable in a real Set-A probe route without adding
app-specific engine logic. Candidate routes:

1. fixed-radius grouped/self-query probe route used by RTDBSCAN/Hausdorff/
   Barnes-Hut stress rows;
2. AABB native query-handle prepared-session route used by LibRTS/contact
   manifold probes;
3. grouped reduction/component continuation route used by RayDB/RTDBSCAN/
   Triangle probes.

M1.2 makes the productized runner path visible inside the CuPy grouped-stream
Set-A probe route. Pod A/B is now meaningful for that route only, not for a
full all-app release run.

## Goal-Level Decision Audit

Decision: bind the prepared execution/session runner to the generic fixed-radius
self-query primitive family, while keeping release blocked.

1. Was I foolish?
   No for this decision. It directly follows the external review's Gap-1
   redirect: make a productized execution path actually execute a real generic
   primitive.
2. If yes, what actions made the decision foolish?
   The foolish action would be to treat this local contract binding as a
   performance win or as release evidence before a real Set-A probe route and
   pod A/B exist.
3. Was there another path that would have avoided getting stuck on this idea?
   Yes: keep polishing caches or rerun all apps immediately. The current
   evidence says that path mostly reaches parity and spends pod time before the
   architecture is executing.
4. Can I now try a different path that actually solves the problem?
   Yes. Use this binding as the first runner-backed primitive, then wire the
   same runner spine into real Set-A probe routes and measure only after that
   path is visible.
