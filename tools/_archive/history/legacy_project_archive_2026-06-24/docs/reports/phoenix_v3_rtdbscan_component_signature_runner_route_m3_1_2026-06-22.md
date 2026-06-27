# Phoenix V3 RTDBSCAN Component-Signature Runner Route M3.1

Date: 2026-06-22
Status: real benchmark route wired through productized runner; local route
contract passed; not pod evidence; not release evidence.

## Summary

The existing RTDBSCAN grouped-stream Numba column-signature route now goes
through the generic Phoenix V3 prepared execution/session runner:

```text
route: examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py
mode: optix_rt_core_grouped_stream_numba_column_signature_3d
helper: run_radius_graph_component_signature_3d_prepared_session
productized_execution_path: prepared_execution_session_runner
primitive_family: fixed_radius_graph_component_signature
continuation_contract: grouped_stream_component_size_signature_3d
```

No RTDBSCAN-specific native ABI was added. The route still uses the existing
generic fixed-radius graph component-signature continuation; the benchmark app
is only the probe that exposes it.

## What Changed

For Numba grouped-stream column-signature modes, the benchmark app now:

- creates an explicit `ExplicitPreparedSessionCache`;
- calls `run_radius_graph_component_signature_3d_prepared_session`;
- preserves compact component-size signature output without Python row
  materialization;
- records `prepared_execution_session_runner_used`;
- records runtime-executed and cache-hit counts; and
- keeps all release/public/broad/true-zero-copy/automatic-selection/app-native
  flags false.

Other grouped-stream routes keep their previous path.

## Boundaries

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
automatic_partner_selection_authorized: false
app_specific_native_engine_logic_allowed: false
pod_performance_evidence: false
full_all_app_rerun_authorized_by_this_packet: false
```

This is route wiring plus local contract evidence only. It is not a second
Set-A material win until a focused same-hardware pod A/B shows the measured win
comes from `prepared_execution_session_runner`.

## Verification

```text
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_rtdbscan_component_signature_optimization_test tests.v3_phoenix_prepared_execution_session_runner_test tests.v3_phoenix_next_dominant_hotpath_selection_test
Ran 21 tests
OK
```

The new route test executes the real RTDBSCAN app branch with a fake runner and
checks:

- `prepared_execution_session_runner_used: true`;
- `productized_execution_path: prepared_execution_session_runner`;
- `prepared_execution_session_runner_runtime_executed_count: 3`;
- `prepared_execution_session_runner_cache_hit_count: 2`;
- compact `numba_direct_component_signature_counts`;
- no neighbor-row or Python-row materialization for the signature path; and
- all release/public/broad/true-zero-copy/automatic-selection/app-native flags
  false.

## Next Work

1. Run focused same-hardware pod A/B for this route only.
2. Accept this as the second Set-A focused probe only if route metadata proves
   `productized_execution_path: prepared_execution_session_runner` and wall
   speedup clears the current focused lower bound (`>= 1.15x`, `1.20x`
   preferred).
3. Do not run full all-app until at least two Set-A probes have runner-backed
   focused evidence and Set A / Set B membership is frozen.

## Goal-Level Decision Audit

Decision: wire the existing RTDBSCAN grouped-stream Numba column-signature
route through the generic productized runner before spending pod time.

1. Was I foolish?
   No for this decision. It converts the local generic helper into a real
   benchmark route while preserving the shared runtime boundary.
2. What actions would have made this foolish?
   It would be foolish to add an RTDBSCAN-native ABI, rename a benchmark
   shortcut as a language feature, or treat local fake-runner evidence as
   performance proof.
3. Was there another path?
   Yes. I could have gone straight to pod or patched the old route directly,
   but that would repeat the old pattern of performance work without a visible
   productized execution path.
4. Can I now try a different path that truly solves the problem?
   Yes. The next path is a focused pod A/B that must prove the measured route
   uses the productized runner and wins materially before any broader rerun.
