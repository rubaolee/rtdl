# Phoenix V3 Repeated Prepared-Session Runner M3.3

Date: 2026-06-22
Status: `local_contract_progress_not_release_authorization`
Scope: Phoenix V3 generic runtime work only.

## Summary

Phoenix V3 now has a productized repeated prepared-session runner API:

```text
run_repeated_prepared_execution_session(...)
```

This closes a local runtime-contract gap identified by the performance-failure
accounting: the runner can now perform one cache lookup / prepare phase, then
execute warmup plus N measured prepared operations inside one runner call, and
emit one prepared-execution report after the measured repeats.

This is not pod evidence, not a release authorization, not a broad V3-over-V2
claim, and not the missing second Set-A material win.

## Why This Was Needed

The M3.1 RTDBSCAN runner path failed because productizing the path added
wrapper overhead around an already-fast legacy route:

```text
M3.1 runner_vs_legacy: 0.5038x
M3.2 runner_vs_legacy: 0.9930x after fingerprint/overhead repair
```

M3.2 recovered parity, but parity recovery is not V3 performance. The next
generic mechanism needed by V3 is a runner shape that matches how the legacy
fast routes are actually used:

```text
prepare once
lookup/cache once
warm up
run measured repeats inside the prepared session
report once
```

Before M3.3, callers could only call the runner one prepared execution at a
time, which encouraged app-level repeat loops and repeated runner/report
overhead.

## What Changed

Code changes:

```text
src/rtdsl/prepared_execution.py
src/rtdsl/__init__.py
tests/v3_phoenix_prepared_execution_session_runner_test.py
```

New exported API:

```text
run_repeated_prepared_execution_session(task, measured_repeat_count=...)
```

Package surface check:

```text
import rtdsl as rt
rt.PreparedExecutionSessionTask
rt.PreparedExecutionSessionResult
rt.run_prepared_execution_session
rt.run_repeated_prepared_execution_session
rt.run_fixed_radius_count_threshold_3d_self_query_prepared_session
rt.run_aabb_index_query_2d_range_intersection_prepared_session
rt.run_radius_graph_component_signature_3d_prepared_session
```

The repeated runner records:

```text
repeated_prepared_session_execution: true
measured_repeat_count
measured_repeat_seconds
measured_total_sec
measured_median_sec
measured_best_sec
single_cache_lookup_for_measured_repeats: true
single_report_after_measured_repeats: true
per_iteration_task_reconstruction_avoided: true
per_iteration_fingerprint_recompute_avoided: true
```

The existing single-run API remains:

```text
run_prepared_execution_session(task)
```

and now shares the same internal execution path with `measured_repeat_count=1`.

The generic helper routes also accept `measured_repeat_count` while preserving
their default behavior:

```text
run_fixed_radius_count_threshold_3d_self_query_prepared_session(..., measured_repeat_count=1)
run_aabb_index_query_2d_range_intersection_prepared_session(..., measured_repeat_count=1)
run_radius_graph_component_signature_3d_prepared_session(..., measured_repeat_count=1)
```

## Contract Boundaries

All existing Phoenix V3 claim boundaries remain false:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
automatic_partner_selection_authorized: false
app_specific_native_engine_logic_allowed: false
```

The runner still requires:

```text
explicit backend
explicit partner
explicit cache
generic primitive name
caller-supplied prepare/run functions
```

App-shaped primitive names remain rejected through the prepared-session cache
key contract.

## Validation

Focused local test:

```text
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test
```

Result:

```text
Ran 13 tests
OK
```

Adjacent focused regression check:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_rtdbscan_component_signature_optimization_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test

Ran 18 tests
OK
```

External review:

```text
review: docs/reviews/claude_phoenix_v3_repeated_prepared_session_runner_m3_3_review_2026-06-22.md
verdict: approve_with_required_edits_not_release
required_edits_applied: true
```

Required edits applied after review:

```text
PREPARED_EXECUTION_SESSION_RUNNER_VERSION:
  rtdl.v3.phoenix.prepared_execution_session_runner.m3_3
measured_repeat_count=0 rejection test:
  test_repeated_runner_rejects_zero_measured_repeat_count
```

New test:

```text
test_repeated_runner_executes_measured_repeats_inside_one_session_call
```

It verifies:

```text
one prepare/cache lookup
one prepared value reused
one warmup run
four measured prepared runs
four executor repeat timings
one prepared-execution report
no release/public/broad/zero-copy claims
```

## What This Does Not Prove

This does not prove:

- V3 is faster than V2.14;
- RTDBSCAN is now faster;
- AABB M2.1 generalizes;
- a second material Set-A productized-path probe exists;
- another full all-app pod run is authorized.

The current Set A / Set B gate remains:

```text
all_app_pod_spend_authorized: false
release_candidate_under_two_number_bar: false
focused material productized probes: 1 / 2 required
```

## Next Required Work

1. Wire this repeated runner into one real Set-A route without app-specific
   native engine logic.
2. Run focused same-pod A/B only for that route.
3. Treat the result as material only if it beats the relevant incumbent route,
   not merely Embree or a weaker control.
4. Keep all release and public performance flags false unless the frozen gate
   later authorizes broader evidence.

## Goal-Level Decision Audit

Decision: implement the generic repeated prepared-session runner before
spending more pod time.

1. Was I foolish?
   No. This directly targets a measured Phoenix V3 failure mode: runner overhead
   and app-local repeat loops.
2. If yes, what actions made the decision foolish?
   The foolish action would have been to run another full pod benchmark or add
   an app-specific shortcut before fixing the shared runner shape.
3. Was there another path that avoids being stuck on a foolish idea?
   Yes. The alternative was to keep optimizing isolated benchmark routes, but
   that would preserve the same failure: no user-responsible shared V3 runtime
   surface.
4. Can I now try a different path that truly solves the problem?
   Yes. The next path is to wire this repeated runner into a real Set-A probe,
   then require focused same-pod evidence before any broader claim.
