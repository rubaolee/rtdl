# Call For Review: Phoenix V3 RTDBSCAN Repeated Runner Route M3.4

Date: 2026-06-22
Requested reviewer: Claude
Protocol: one bounded automated attempt; record quota/tool failure if unavailable.

## Review Request

Please critically review M3.4: wiring the M3.3 repeated prepared-session runner
into the real RTDBSCAN component-signature Set-A route.

Controlling context:

- Phoenix V3 remains `redo_required`.
- M3.1 RTDBSCAN runner-vs-legacy was `0.5038x`.
- M3.2 recovered runner-vs-legacy to `0.9930x`, parity only.
- M3.3 added `run_repeated_prepared_execution_session(...)` and was reviewed
  as local contract progress, not release.
- M3.4 should only be judged as local route wiring. It is not pod evidence.

## Files To Review

```text
src/rtdsl/prepared_execution.py
examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py
tests/v3_phoenix_rtdbscan_component_signature_optimization_test.py
docs/reports/phoenix_v3_rtdbscan_repeated_runner_route_m3_4_2026-06-22.md
docs/reviews/codex_phoenix_v3_repeated_prepared_session_runner_m3_3_2ai_consensus_2026-06-22.md
```

## What Changed

The RTDBSCAN route no longer loops over the single-run productized runner:

```text
for iteration in range(repeat):
    run_radius_graph_component_signature_3d_prepared_session(...)
```

Instead it calls the generic helper once:

```text
run_radius_graph_component_signature_3d_prepared_session(
    ...,
    warmup_count=warmup,
    measured_repeat_count=repeat - warmup,
    retain_repeat_outputs=True,
)
```

The route then reconstructs measured rows from retained repeat outputs and
`measured_repeat_seconds` in runner metadata.

## Validation Already Run

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_rtdbscan_component_signature_optimization_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test

Ran 18 tests
OK
```

The local real-route smoke was attempted but blocked by local Windows
environment:

```text
ModuleNotFoundError: No module named 'numba'
```

## Questions

1. Does M3.4 correctly use the generic repeated runner, rather than adding
   app-specific RTDBSCAN native logic?
2. Is the route metadata honest now that one runner call covers N measured
   repeats?
3. Are there any timing/accounting fields that look misleading before pod A/B?
4. Is this only local route-contract progress, not pod evidence and not a Set-A
   material win?
5. What edits are required before a focused same-pod M3.4 A/B would be
   justified?

## Expected Verdict Labels

Use one:

```text
approve_route_contract_not_release
approve_with_required_edits_not_release
reject_needs_redesign
blocked_review_not_obtained
```

Explicitly state:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_rerun_authorized: false
focused_m3_4_pod_ab_authorized: true_or_false
```
