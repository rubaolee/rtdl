# Call For Review: Phoenix V3 M19 Triangle Environment-Corrected Replacement Run

Date: 2026-06-22

Status: `request_m19_env_corrected_replacement_pod_authorization`

This review asks one narrow question: after the single M18 focused Triangle POD
authorization was consumed by a wrong-interpreter environment failure, is one
environment-corrected replacement run authorized using the verified project
venv?

This does not authorize release, public speedup wording, broad V3-over-V2
wording, all-app POD, V4 work, true zero-copy, or external embedding.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
focused_pod_spend_authorized_now: review_requested_only
third_strict_set_a_material_probe_closed: false
```

## Packet

- M18 harness JSON:
  `docs/rebuild/v3/phoenix_v3_m18_triangle_runner_harness_2026-06-22.json`
- M18 harness report:
  `docs/reports/phoenix_v3_m18_triangle_runner_harness_2026-06-22.md`
- M18 failed POD intake:
  `docs/reports/phoenix_v3_m18_triangle_focused_pod_failed_env_intake_2026-06-22.md`
- M18 final authorization consumed by attempt 1:
  `docs/reviews/codex_bernoulli_phoenix_v3_m18_triangle_runner_harness_final_pod_authorization_2026-06-22.md`
- Attempt 1 evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_triangle_runner_m18_focused_pod_ab_20260622/`
- Harness:
  `scripts/v3_phoenix_triangle_runner_m18_pod_ab.py`
- M16/M17/M18 packet tests:
  `tests/v3_phoenix_m18_triangle_runner_harness_packet_test.py`
  `tests/v3_phoenix_triangle_runner_m18_pod_ab_test.py`

## Attempt 1 Facts

Attempt 1 used:

```text
PYTHONPATH=src:. python3 scripts/v3_phoenix_triangle_runner_m18_pod_ab.py --output-dir docs/rebuild/v3/evidence/phoenix_v3_triangle_runner_m18_focused_pod_ab_20260622 --edge-file build/phoenix_v3_m18_triangle/k4_cliques_80000.edge --cliques 80000 --partner cupy --warmup 1 --repeat 5 --require-rt-hardware --generate-edge-file
```

It failed closed:

```text
failed_check_count: 6
variant_count: 2
comparisons: {}
edge_file_preflight_status: pass
edge_file_sha256: 8bc1bd3fc75d86707d326fc4e2913cae7d6c380c5afa788f08b5bdbb18127005
rt_hardware_gate_status: pass
embree_same_contract_control: oracle matched, query_median_ms=543.298989534378
legacy_app_front_door_optix: ModuleNotFoundError: No module named 'cupy'
productized_prepared_execution_runner: ModuleNotFoundError("No module named 'cupy'")
```

Read-only environment diagnosis after the attempt:

```text
/root/rtdl_v3_rebuild_20260620/.venv/bin/python
cupy present
numba present
```

Additional no-benchmark venv smoke:

```text
PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python -m py_compile scripts/v3_phoenix_triangle_runner_m18_pod_ab.py src/rtdsl/prepared_execution.py
PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python -c "import cupy, numba; import scripts.v3_phoenix_triangle_runner_m18_pod_ab as m; print('venv-smoke-ok', m.STATUS_NOT_RELEASE)"
result: venv-smoke-ok triangle_runner_m18_harness_ready_not_pod_authorized
```

Interpretation:

```text
first_authorization_consumed: true
performance_evidence_obtained: false
failure_class: wrong_interpreter_environment_failure
productized_runner_speed_result: none
third_strict_set_a_material_probe_closed: false
```

## Proposed Replacement Command

If and only if authorized by this review, run exactly once with a new output
directory:

```text
cd /root/rtdl_v3_rebuild_20260620/current &&
PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python scripts/v3_phoenix_triangle_runner_m18_pod_ab.py \
  --output-dir docs/rebuild/v3/evidence/phoenix_v3_triangle_runner_m18_focused_pod_ab_venv_20260622 \
  --edge-file build/phoenix_v3_m18_triangle/k4_cliques_80000.edge \
  --cliques 80000 \
  --partner cupy \
  --warmup 1 \
  --repeat 5 \
  --require-rt-hardware \
  --generate-edge-file
```

## Success And Stop Rules

The replacement run must preserve the M17/M18 bars:

- all variants match `oracle_triangle_count=320000`;
- runner metadata shows `runtime_executed=true`,
  `productized_execution_path=prepared_execution_session_runner`, and
  `runtime_trunk_executes_end_to_end=true`;
- runner OptiX beats Embree same-contract control by at least `1.20x` on hot
  query median and runner-inclusive wall before Triangle can be considered a
  material Set-A candidate;
- runner-inclusive wall is at least `0.98x` of legacy app-front-door OptiX;
- all release/public/broad V3-over-V2/V4/zero-copy/all-app flags remain false.

Stop immediately after this one run and copy evidence back. Do not run all-app,
do not rerun until it looks better, and do not broaden the claim.

## Requested Verdict Labels

Choose exactly one:

- `authorize_m19_one_env_corrected_triangle_replacement_pod`: one replacement
  focused Triangle POD run is authorized because attempt 1 failed before the
  intended CuPy/OptiX paths ran, the venv has the required packages, and the
  proposed command preserves the same row, bars, and cap.
- `deny_m19_replacement_pod_use_local_only`: do not spend POD; require more
  local or remote no-benchmark gates first.
- `revise_m19_packet`: require specific edits before deciding.
- `reject_m19_path`: the Triangle replacement-run path should stop.

Regardless of verdict, explicitly state:

- release authorization: yes/no
- public speedup authorization: yes/no
- broad V3-over-V2 authorization: yes/no
- focused replacement POD authorization now: yes/no
- all-app POD authorization now: yes/no
- whether attempt 1 can be interpreted as performance evidence
- whether Triangle counts as the third strict Set-A material probe now

## Goal-Level Decision Audit

Decision: ask external review before spending a replacement focused POD run
after the consumed wrong-interpreter attempt.

1. Was I foolish?
   Yes.
2. If yes, what actions made the decision foolish?
   The first POD attempt used generic `python3` without a preflight package
   check against the historical project venv.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Verify interpreter/package state first, then launch only with the
   verified venv.
4. Can I now try a different path that actually solves the problem?
   Yes. Use this packet to obtain a strict verdict; if approved, run exactly
   one venv-based replacement and stop for evidence intake.
