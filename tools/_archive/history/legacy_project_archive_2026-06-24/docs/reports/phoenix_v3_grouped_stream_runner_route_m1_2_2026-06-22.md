# Phoenix V3 Grouped-Stream Runner Route M1.2

Date: 2026-06-22
Status: `m1_2_runner_backed_fixed_radius_probe_route_validated_not_release`

## Summary

This report records the first real Set-A probe route wired through the Phoenix
V3 prepared execution/session runner.

Files changed:

- `src/rtdsl/partner_adapters.py`
- `tests/v3_phoenix_fixed_radius_graph_self_query_refresh_test.py`

The CuPy grouped-stream route:

```text
PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D.run
```

now refreshes fixed-radius core flags through:

```text
run_fixed_radius_count_threshold_3d_self_query_prepared_session
```

instead of directly calling the low-level fixed-radius self-query adapter.

This keeps the benchmark app as a probe. The change is in the generic
runtime/partner-adapter layer, not in an app-specific engine path.

Follow-up pod A/B:

```text
docs/reports/phoenix_v3_grouped_stream_runner_route_pod_ab_2026-06-22.md
status: m1_2_runner_route_pod_ab_neutral_not_release
geomean before/after speedup: 0.9979x
interpretation: route evidence, not performance win
```

## What Is Now True

- The productized runner path is visible in a real grouped-stream probe route.
- The route records `prepared_execution_session_runner_used: true`.
- The route records `productized_execution_path: prepared_execution_session_runner`.
- The route records `core_flag_refresh_runtime_executed` from the runner
  metadata.
- The route preserves the existing fixed-radius self-query adapter and output
  column contract.
- The route keeps release/public/broad/true-zero-copy speed claims false.
- Numba grouped-stream is not marked as runner-backed; it still has separate
  PTX/toolkit risk and must not inherit CuPy route claims.

## Validation

Current V3/M1.2 local gates:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_fixed_radius_graph_self_query_refresh_test \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_next_dominant_hotpath_selection_test

17 tests OK
```

Compile gate:

```text
PYTHONPATH=src;. py -3 -m py_compile \
  src/rtdsl/prepared_execution.py \
  src/rtdsl/partner_adapters.py

OK
```

Protocol/release gates:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_external_verdict_intake_test \
  tests.v3_phoenix_major_performance_mandate_gate_test \
  tests.v3_phoenix_release_readiness_gate_test \
  tests.v3_release_wording_gate_test

16 tests OK
```

Legacy grouped-stream tests that read the old
`examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
file are not counted here because that file is absent in the current tree. This
is an existing fixture/state issue, not M1.2 evidence.

## Non-Claims

This packet does not claim:

- V3 is release-ready.
- V3 broadly beats V2.x.
- The runner-backed route is faster.
- Another full all-app pod run is authorized.
- True zero-copy is implemented or authorized.
- Numba grouped-stream has the same runner-backed route.
- V4/C ABI/embedding scope belongs in Phoenix V3.

## Next Work

Focused pod A/B for this route is complete and neutral, not winning. The next
step is not a full all-app run. Route a second Set-A family through the runner
or remove measurable runner-level overhead across multiple runner-backed
routes.

Only after this route and at least one second Set-A route show material focused
evidence should another full V2.x vs V3 all-app run be considered.

## Goal-Level Decision Audit

Decision: wire the runner-backed fixed-radius self-query primitive into the real
CuPy grouped-stream probe route, while keeping release blocked.

1. Was I foolish?
   No for this decision. It moves from a local helper contract to a real
   reusable Set-A probe route without app-specific benchmark logic.
2. If yes, what actions made the decision foolish?
   The foolish action would be to claim performance before pod A/B, or to mark
   Numba/other routes as runner-backed without equivalent wiring and evidence.
3. Was there another path that would have avoided getting stuck on this idea?
   Yes: run all apps immediately or keep tuning caches. That would again spend
   evidence budget before the productized execution path is visible.
4. Can I now try a different path that actually solves the problem?
   Yes. Run focused same-pod A/B for this route, then repeat the runner pattern
   on a second Set-A route before any release-scale benchmark.
