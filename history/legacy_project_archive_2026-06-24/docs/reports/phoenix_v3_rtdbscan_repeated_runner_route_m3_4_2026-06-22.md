# Phoenix V3 RTDBSCAN Repeated Runner Route M3.4

Date: 2026-06-22
Status: `local_route_contract_progress_not_pod_evidence_not_release`
Scope: Phoenix V3 generic runtime route wiring only.

## Summary

M3.4 wires the M3.3 repeated prepared-session runner into the real RTDBSCAN
component-signature Set-A route.

Before M3.4, the RTDBSCAN productized runner route still performed:

```text
for iteration in range(repeat):
    run_radius_graph_component_signature_3d_prepared_session(...)
```

That meant the benchmark route still paid runner/cache/report overhead once per
repeat. M3.4 changes the route to perform one productized runner call:

```text
run_radius_graph_component_signature_3d_prepared_session(
    ...,
    warmup_count=warmup,
    measured_repeat_count=repeat - warmup,
    retain_repeat_outputs=True,
)
```

The runner now owns the repeated prepared-session measurement window. The
benchmark route reconstructs measured rows from retained repeat outputs and
runner repeat timings.

## Why This Matters

The controlling RTDBSCAN evidence before this step was:

```text
M3.1 runner_vs_legacy: 0.5038x
M3.2 runner_vs_legacy: 0.9930x
```

M3.2 recovered parity by moving expensive fingerprint work out of the hot path,
but the route still had an app-level runner call loop. M3.4 removes that route
shape so the productized runner can be tested as the repeated prepared-session
runtime, not as repeated single-run wrapper calls.

This is generic runtime work:

- no RTDBSCAN-specific native symbol was added;
- no DBSCAN-specific ABI was added;
- the generic primitive remains `fixed_radius_graph_component_signature_3d`;
- the explicit partner remains `numba`;
- the repeated execution primitive is shared in `src/rtdsl/prepared_execution.py`.

## What Changed

Code files:

```text
src/rtdsl/prepared_execution.py
examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py
tests/v3_phoenix_rtdbscan_component_signature_optimization_test.py
```

Runner/helper API additions used by route:

```text
measured_repeat_count
retain_repeat_outputs
validate_each_repeat
```

RTDBSCAN route metadata now records:

```text
prepared_execution_session_runner_runtime_executed_count: 1
prepared_execution_session_runner_measured_repeat_count: repeat - warmup
prepared_execution_session_runner_repeated_execution: true
prepared_execution_session_runner_single_cache_lookup_for_measured_repeats: true
prepared_execution_session_runner_single_report_after_measured_repeats: true
prepared_execution_session_runner_cache_hit_count: 0
```

The route still records:

```text
prepared_execution_session_runner_used: true
productized_execution_path: prepared_execution_session_runner
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
automatic_partner_selection_authorized: false
app_specific_native_engine_logic_allowed: false
```

## Validation

Focused local validation:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_rtdbscan_component_signature_optimization_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test

Ran 18 tests
OK
```

The RTDBSCAN route test now verifies:

```text
runner call count: 1
measured repeat count: 3
repeated execution metadata: true
single cache lookup metadata: true
single report metadata: true
cache hit count: 0
measured_run_count: 3
all claim flags false
```

Attempted local real-route smoke:

```text
mode: optix_rt_core_grouped_stream_numba_column_signature_3d
dataset: tiny
repeat: 3
warmup: 0
```

Result:

```text
blocked locally: ModuleNotFoundError: No module named 'numba'
```

This is an environment limitation on the Windows local environment, not pod
evidence and not a route correctness proof. The real route still needs focused
same-pod A/B on the RT hardware/partner environment.

## What This Does Not Prove

M3.4 does not prove:

- V3 is faster than V2.14;
- RTDBSCAN is faster than the incumbent legacy OptiX route;
- a second material Set-A productized-path win exists;
- all-app pod rerun is authorized;
- release is authorized.

Current public/release boundaries remain:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
full_all_app_rerun_authorized_by_this_packet: false
second_material_set_a_probe_obtained: false
```

## Next

Run a focused same-pod A/B for RTDBSCAN M3.4 only after review. The comparison
must be against the relevant incumbent legacy OptiX route, not merely Embree.

Success bar:

```text
runner_vs_legacy >= 1.15x for material Set-A candidate
runner_vs_legacy >= 0.98x for parity-preserving route progress
all claim flags false
runner metadata present
signatures stable
```

Failure rule:

```text
If M3.4 remains near parity, stop spending RTDBSCAN time as the second Set-A
material-win path and move to AABB generalization or typed continuation.
```

## Goal-Level Decision Audit

Decision: wire the repeated runner into the real RTDBSCAN route before focused
pod A/B.

1. Was I foolish?
   No. This removes the exact app-level repeat loop that M3.3 was designed to
   eliminate.
2. If yes, what actions made the decision foolish?
   It would have been foolish to run pod A/B while the route still looped over
   single-run runner calls, or to add RTDBSCAN-specific native shortcuts.
3. Was there another path that avoids being stuck on a foolish idea?
   Yes. The alternative was to abandon RTDBSCAN after M3.2 parity and move to
   AABB generalization. That remains valid if M3.4 pod evidence is not
   material.
4. Can I now try a different path that truly solves the problem?
   Yes. M3.4 gives a real repeated-runner route. The next proof must be focused
   same-pod A/B against the incumbent legacy OptiX route.
