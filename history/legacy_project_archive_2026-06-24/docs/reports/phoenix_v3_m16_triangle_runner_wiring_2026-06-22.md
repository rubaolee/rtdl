# Phoenix V3 M16 Triangle Runner Wiring

Date: 2026-06-22

Status: `m16_local_triangle_runner_wiring_validated_not_pod`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
external_embedding_or_zero_copy_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
third_strict_set_a_material_probe_closed: false
```

2-AI verdict: `accept_m16_prepare_m17_focused_pod_protocol_no_run`

Consensus record:
`docs/reviews/codex_bernoulli_phoenix_v3_m16_triangle_runner_wiring_2ai_consensus_2026-06-22.md`

## Bottom Line

M16 adds the missing local productized runner wiring for the Triangle candidate
without spending POD. The new generic helper is:

```text
run_ray_triangle_weighted_summary_device_output_stream_prepared_session
```

It lives in `src/rtdsl/prepared_execution.py`, is exported from
`src/rtdsl/__init__.py`, and is covered by
`tests/v3_phoenix_prepared_execution_session_runner_test.py`.

This is a runtime-trunk implementation step, not a performance result. It does
not count Triangle as the third strict Set-A material probe yet.

## What The Helper Does

The helper routes a generic ray/triangle weighted-summary device-output stream
through the existing Phoenix `prepared_execution_session_runner`:

```text
primitive: ray_triangle_weighted_summary_device_output_stream
workflow: ray_triangle_weighted_summary_device_output_stream_prepared_session
contract: generic_ray_triangle_weighted_any_hit_summary_device_output_stream_v1
backend: optix
partner: explicit user-chosen partner
```

The local contract test verifies that it can produce:

```text
runtime_executed: true
productized_execution_path: prepared_execution_session_runner
runtime_trunk_executes_end_to_end: true
internal_device_residency_between_rtdl_phases: true
device_output_stream_validated: true
hot_path_host_materialization: false
repeat5_material_probe_candidate: true
m113_graph_capture_claim_authorized: false
old_triangle_row_does_not_count_as_current_third_probe: true
```

## Guardrails

The helper rejects:

- non-OptiX backend for this device-output stream helper;
- missing, `none`, `auto`, or automatic partner selection;
- app-shaped output contract names such as `triangle_counting` or `rt_graph`;
- repeat5 material-probe mode when measured repeats are below 5.

It also keeps all release and public-claim flags false.

## Verification

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test
Ran 33 tests
OK

$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v3_phoenix_m15_third_strict_set_a_probe_audit_test tests.v3_release_wording_gate_test
Ran 8 tests
OK

$env:PYTHONPATH='src;.'; py -3 -c "import rtdsl as rt; print(hasattr(rt, 'run_ray_triangle_weighted_summary_device_output_stream_prepared_session'))"
True

$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test tests.v3_phoenix_m16_triangle_runner_wiring_test tests.v3_phoenix_m15_third_strict_set_a_probe_audit_test tests.v3_release_wording_gate_test
Ran 46 tests before the consensus record was added.
OK

After adding the consensus-record test:

$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test tests.v3_phoenix_m16_triangle_runner_wiring_test tests.v3_phoenix_m15_third_strict_set_a_probe_audit_test tests.v3_release_wording_gate_test
Ran 47 tests
OK
```

The local Python installation prints `Could not find platform independent
libraries <prefix>` before these runs, but the commands return success and the
test bodies pass.

## Still Not Closed

M16 does not authorize:

- focused POD;
- all-app POD;
- release;
- public speedup wording;
- broad V3-over-V2 wording;
- true-zero-copy or V4/embedding wording;
- RT-Graph paper reproduction;
- graph database acceleration;
- full Triangle application speedup.

The next controlled step should be M17: a reviewed focused-POD protocol for the
80,000-clique row, comparing the old Triangle route against the runner-backed
generic device-output stream route, with Embree retained as a control and hot
query versus runner-inclusive wall metrics reported separately.

M17 should not run POD unless its own 2-AI review explicitly authorizes one
focused run.

## Goal-Level Decision Audit

Decision: implement local generic ray/triangle weighted-summary device-output
stream runner wiring before any POD spend.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   It would be foolish to run POD before the current Phoenix runner path can
   produce `runtime_executed` and residency metadata.
3. Was there another path?
   Yes: spend POD directly from old Triangle evidence. That would again
   over-count a strong but old row-scoped packet.
4. Can I now try a different path?
   Yes. Use the helper as the local productized path, request 2-AI review, and
   only then decide whether focused POD is authorized.
