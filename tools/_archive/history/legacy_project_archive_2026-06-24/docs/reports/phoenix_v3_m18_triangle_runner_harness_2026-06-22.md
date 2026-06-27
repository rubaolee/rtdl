# Phoenix V3 M18 Triangle Runner Harness

Date: 2026-06-22

Status: `m19_env_corrected_triangle_focused_pod_accepted_third_strict_set_a_probe`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
third_strict_set_a_material_probe_closed: false
```

## Bottom Line

M18 implements the local Triangle focused A/B harness requested by the M17
review. Bernoulli later authorized exactly one focused POD run; that
authorization was consumed, but the run failed before the CuPy/OptiX variants
could produce payloads because the command used `/usr/bin/python3` instead of
the historical project venv.

The consumed attempt is recorded separately:

```text
docs/reports/phoenix_v3_m18_triangle_focused_pod_failed_env_intake_2026-06-22.md
```

No Triangle performance conclusion, third Set-A material probe closure, release
authorization, public speedup wording, broad V3-over-V2 wording, or all-app POD
authorization follows from that failed attempt.

Claude then authorized one environment-corrected replacement run after a
subprocess-interpreter pre-launch check. That M19 run passed and is recorded in:

```text
docs/reports/phoenix_v3_m19_triangle_env_corrected_pod_result_2026-06-22.md
```

It is focused productized-runner evidence only. Claude result review later
accepted it as closing Triangle as the third strict Set-A material probe.

The new script is:

```text
scripts/v3_phoenix_triangle_runner_m18_pod_ab.py
```

It supports three variants:

```text
embree_same_contract_control
legacy_app_front_door_optix
productized_prepared_execution_runner
```

The runner variant uses the M16 helper:

```text
run_ray_triangle_weighted_summary_device_output_stream_prepared_session
```

and the device-output executor:

```text
prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor
```

so the intended POD run measures the current Phoenix productized runner path,
not only the old Triangle app-front-door route.

## Initial Review And Fix

Bernoulli's initial M18 verdict was `revise_m18_harness`.

Blocking issue:

```text
The first draft read weighted_hit_sum_out.get() inside the measured runner body
while claiming hot_path_host_materialization=false.
```

Fix:

```text
run_ray_triangle_weighted_summary_device_output_stream_prepared_session now
accepts finalize_weighted_summary.

launch_weighted_summary_device_output_stream now enqueues/synchronizes the
device-output executor only.

finalize_weighted_summary_device_output_stream reads weighted_hit_sum_out once
after measured repeats.
```

Regression coverage:

```text
tests.v3_phoenix_triangle_runner_m18_pod_ab_test.test_host_scalar_read_is_finalize_only_not_measured_launch_body
tests.v3_phoenix_prepared_execution_session_runner_test.test_ray_triangle_weighted_summary_helper_can_finalize_scalar_after_measured_repeats
```

Bernoulli's second M18 verdict was also `revise_m18_harness`.

Second-review blockers:

```text
failure_checks checked only the productized runner oracle status, not Embree
or legacy controls.

the K4 edge file had no checksum recording/enforcement before variants.
```

Second fix:

```text
real runs now compute the expected K4 binary edge-file sha256, actual sha256,
edge count, and byte count before variants run.

real runs stop before variants when the edge-file identity preflight fails.

failure_checks now requires Embree, legacy OptiX, and productized runner
payloads to expose and match oracle_triangle_count.
```

## Local Verification

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v3_phoenix_triangle_runner_m18_pod_ab_test
Ran 6 tests
OK

$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test tests.v3_phoenix_triangle_runner_m18_pod_ab_test
Ran 40 tests
OK

$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test tests.v3_phoenix_triangle_runner_m18_pod_ab_test tests.v3_phoenix_m18_triangle_runner_harness_packet_test tests.v3_phoenix_m17_triangle_focused_pod_protocol_test tests.v3_phoenix_m16_triangle_runner_wiring_test
Ran 58 tests
OK

$env:PYTHONPATH='src;.'; py -3 scripts\v3_phoenix_triangle_runner_m18_pod_ab.py --output-dir build\phoenix_v3_m18_triangle_dry_run --edge-file build\phoenix_v3_m18_triangle_dry_run\k4.edge --cliques 80000 --repeat 5 --warmup 1 --dry-run
status: triangle_runner_m18_harness_ready_not_pod_authorized
failed_check_count: 0
variant_count: 3
pod_run_authorized_by_m18: false
edge_file_preflight_status: dry_run_not_required

py -3 scripts\v3_release_wording_gate.py --pretty
status: pass
violations: []

py -3 -m py_compile scripts\v3_phoenix_triangle_runner_m18_pod_ab.py src\rtdsl\prepared_execution.py
OK
```

The dry-run artifact is:

```text
build/phoenix_v3_m18_triangle_dry_run/summary.json
```

## Final M18 POD Authorization And Attempt 1 Intake

Bernoulli's final M18 verdict was:

```text
accept_m18_authorize_one_focused_triangle_pod
authorized_run_count: 1
hard_cap: 2 h / $0.50
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_authorized: false
```

The authorized attempt was run with:

```text
PYTHONPATH=src:. python3 scripts/v3_phoenix_triangle_runner_m18_pod_ab.py --output-dir docs/rebuild/v3/evidence/phoenix_v3_triangle_runner_m18_focused_pod_ab_20260622 --edge-file build/phoenix_v3_m18_triangle/k4_cliques_80000.edge --cliques 80000 --partner cupy --warmup 1 --repeat 5 --require-rt-hardware --generate-edge-file
```

The run failed closed:

```text
failed_check_count: 6
variant_count: 2
comparisons: {}
edge_file_preflight_status: pass
edge_file_sha256: 8bc1bd3fc75d86707d326fc4e2913cae7d6c380c5afa788f08b5bdbb18127005
rt_hardware_gate_status: pass
embree_same_contract_control: oracle matched
legacy_app_front_door_optix: ModuleNotFoundError: No module named 'cupy'
productized_prepared_execution_runner: ModuleNotFoundError("No module named 'cupy'")
```

Read-only diagnosis after the failure:

```text
/root/rtdl_v3_rebuild_20260620/.venv/bin/python
cupy present
numba present
```

Interpretation:

```text
attempt_1_status: failed_wrong_interpreter_no_performance_evidence
first_authorization_consumed: true
performance_interpretation_allowed: false
replacement_run_authorized_now: false
```

## Environment-Corrected Replacement Command

The original M18 report did not authorize this replacement command. It was
later authorized by the M19 Claude review and Codex+Claude consensus, then run
exactly once.

```text
PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python scripts/v3_phoenix_triangle_runner_m18_pod_ab.py --output-dir docs/rebuild/v3/evidence/phoenix_v3_triangle_runner_m18_focused_pod_ab_venv_20260622 --edge-file build/phoenix_v3_m18_triangle/k4_cliques_80000.edge --cliques 80000 --partner cupy --warmup 1 --repeat 5 --require-rt-hardware --generate-edge-file
```

## M19 Environment-Corrected Replacement Result

Claude authorized exactly one replacement run:

```text
docs/reviews/claude_phoenix_v3_m19_triangle_env_corrected_rerun_review_2026-06-22.md
verdict: authorize_m19_one_env_corrected_triangle_replacement_pod
```

Codex accepted the verdict after the required subprocess interpreter check:

```text
docs/reviews/codex_claude_phoenix_v3_m19_triangle_env_corrected_rerun_2ai_consensus_2026-06-22.md
prelaunch_subprocess_interpreter_check: pass
```

The run used the verified project venv:

```text
PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python scripts/v3_phoenix_triangle_runner_m18_pod_ab.py --output-dir docs/rebuild/v3/evidence/phoenix_v3_triangle_runner_m18_focused_pod_ab_venv_20260622 --edge-file build/phoenix_v3_m18_triangle/k4_cliques_80000.edge --cliques 80000 --partner cupy --warmup 1 --repeat 5 --require-rt-hardware --generate-edge-file
```

Result:

```text
exit_code: 0
failed_check_count: 0
variant_count: 3
all_variant_oracle_checks_passed: true
edge_file_sha256: 8bc1bd3fc75d86707d326fc4e2913cae7d6c380c5afa788f08b5bdbb18127005
productized_execution_path: prepared_execution_session_runner
runtime_executed: true
runtime_trunk_executes_end_to_end: true
internal_device_residency_between_rtdl_phases: true
hot_path_host_materialization: false
weighted_hit_sum: 320000
```

Focused comparisons:

```text
runner_vs_embree_hot_speedup: 2414.807809480132x
runner_vs_embree_wall_speedup: 13.408780700958467x
runner_vs_legacy_hot_speedup: 6.962099125364431x
runner_vs_legacy_wall_speedup: 2.1167140613609914x
```

Current interpretation:

```text
M19 focused Triangle result passes the strict focused M17/M18 bars.
third_strict_set_a_material_probe_closed: true
result_review: accept_m19_triangle_third_strict_set_a_probe
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
```

The script has fail-closed gates:

- `repeat >= 5`;
- `cliques >= 80000` unless an explicit smoke flag is used;
- OptiX RT hardware gate with `--require-rt-hardware`;
- K4 edge-file sha256, byte count, and edge count before real variants;
- all three variants matching `oracle_triangle_count`;
- required CuPy/Numba and OptiX symbols;
- M16 `runtime_trunk_executes_end_to_end` metadata;
- heartbeat output for subprocess variants and the in-process runner variant.

## Success Bars

- All variants match `oracle_triangle_count=320000`.
- Runner metadata shows `runtime_executed=true`,
  `productized_execution_path=prepared_execution_session_runner`, and
  `runtime_trunk_executes_end_to_end=true`.
- Runner OptiX beats Embree same-contract control by at least `1.20x` on hot
  query median and runner-inclusive wall.
- Runner-inclusive wall is at least `0.98x` of the legacy app-front-door OptiX
  route.
- Release, public speedup, broad V3-over-V2, V4, zero-copy, and all-app flags
  remain false.

## Budget If Authorized

```text
focused POD wall time: 0.75-1.5 h
focused POD cost at $1 / 4 h: $0.19-$0.38
hard cap before new review: 2 h / $0.50
all-app POD: not authorized
```

## Goal-Level Decision Audit

Decision: record the consumed focused POD attempt as wrong-interpreter
environment failure and seek 2-AI authorization before any replacement run.

1. Was I foolish?
   Yes.
2. If yes, what actions made the decision foolish?
   I used generic `python3` on the POD without first verifying the historical
   project venv that earlier GPU work used, so the single focused authorization
   was consumed before CuPy paths could run.
3. Was there another path?
   Yes: run a read-only interpreter/package gate first and substitute the
   verified venv interpreter into the command before launch.
4. Can I now try a different path?
   Yes. Preserve the failed artifacts, keep all claims blocked, and ask 2-AI
   for a narrowly scoped venv-based replacement run.
