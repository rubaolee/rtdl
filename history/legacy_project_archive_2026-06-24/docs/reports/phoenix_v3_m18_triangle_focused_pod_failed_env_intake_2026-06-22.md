# Phoenix V3 M18 Triangle Focused POD Attempt 1 Failed Environment Intake

Date: 2026-06-22

Status: `focused_pod_attempt_1_consumed_failed_wrong_interpreter_no_performance_evidence`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
focused_pod_spend_authorized_now: false
third_strict_set_a_material_probe_closed: false
```

## Bottom Line

The single M18 focused Triangle POD run authorized by Bernoulli was consumed,
but it did not produce performance evidence. The run used `/usr/bin/python3`,
which lacks CuPy. The historical project venv at
`/root/rtdl_v3_rebuild_20260620/.venv/bin/python` does contain both CuPy and
Numba.

Therefore this attempt is an environment/intake failure, not a Triangle speed
result, not a productized-runner failure, and not release evidence.

## Authorization That Was Consumed

Authorization record:

```text
docs/reviews/codex_bernoulli_phoenix_v3_m18_triangle_runner_harness_final_pod_authorization_2026-06-22.md
verdict: accept_m18_authorize_one_focused_triangle_pod
authorized_run_count: 1
hard_cap: 2 h / $0.50
all_app_pod_authorized: false
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

Command executed:

```text
cd /root/rtdl_v3_rebuild_20260620/current &&
PYTHONPATH=src:. python3 scripts/v3_phoenix_triangle_runner_m18_pod_ab.py \
  --output-dir docs/rebuild/v3/evidence/phoenix_v3_triangle_runner_m18_focused_pod_ab_20260622 \
  --edge-file build/phoenix_v3_m18_triangle/k4_cliques_80000.edge \
  --cliques 80000 \
  --partner cupy \
  --warmup 1 \
  --repeat 5 \
  --require-rt-hardware \
  --generate-edge-file
```

## Evidence Artifacts

Copied local evidence directory:

```text
docs/rebuild/v3/evidence/phoenix_v3_triangle_runner_m18_focused_pod_ab_20260622/
```

Key files:

```text
summary.json
README.md
embree_same_contract_control.json
embree_same_contract_control.stdout.json
embree_same_contract_control.stderr.txt
legacy_app_front_door_optix.json
legacy_app_front_door_optix.stdout.json
legacy_app_front_door_optix.stderr.txt
productized_prepared_execution_runner.error.txt
```

## What Passed

The serious input identity gates passed:

```text
cliques: 80000
edge_count: 480000
oracle_triangle_count: 320000
edge_file_preflight_status: pass
edge_file_sha256: 8bc1bd3fc75d86707d326fc4e2913cae7d6c380c5afa788f08b5bdbb18127005
edge_file_generated_now: true
```

The RT hardware gate passed:

```text
gpu: NVIDIA RTX 4000 Ada Generation
driver: 550.127.05
compute_cap: 8.9
require_rt_hardware: true
status: pass
```

The Embree same-contract control completed and matched the oracle:

```text
oracle_triangle_count: 320000
observed_triangle_count: 320000
triangle_count_matches_oracle: true
query_median_ms: 543.298989534378
wrapper_wall_sec: 11.217252418398857
```

## What Failed

The run failed closed with:

```text
failed_check_count: 6
failed_checks:
  - variant_run_errors_present
  - missing_variants:productized_prepared_execution_runner
  - legacy_app_front_door_optix_status_not_ok
  - legacy_app_front_door_optix_oracle_mismatch
  - productized_prepared_execution_runner_status_not_ok
  - productized_prepared_execution_runner_oracle_mismatch
```

Both OptiX/CuPy paths failed before producing payloads:

```text
legacy_app_front_door_optix:
  ModuleNotFoundError: No module named 'cupy'

productized_prepared_execution_runner:
  ModuleNotFoundError("No module named 'cupy'")
```

The summary recorded only two variants because the productized runner payload
could not be produced:

```text
variant_count: 2
comparisons: {}
all_variant_oracle_checks_passed: false
```

## Environment Diagnosis

The failing run used:

```text
/usr/bin/python3
```

That interpreter has no CuPy/Numba. A follow-up read-only diagnosis found that
the project venv does have both:

```text
/root/rtdl_v3_rebuild_20260620/.venv/bin/python
cupy present
numba present
```

This proves the immediate failure mode was interpreter selection, not a missing
POD package installation and not evidence that the productized runner is slow.

Additional no-benchmark venv smoke passed:

```text
PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python -m py_compile scripts/v3_phoenix_triangle_runner_m18_pod_ab.py src/rtdsl/prepared_execution.py
PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python -c "import cupy, numba; import scripts.v3_phoenix_triangle_runner_m18_pod_ab as m; print('venv-smoke-ok', m.STATUS_NOT_RELEASE)"
result: venv-smoke-ok triangle_runner_m18_harness_ready_not_pod_authorized
```

## Interpretation

This attempt cannot be used for:

- Triangle OptiX-vs-Embree speedup;
- productized runner-vs-legacy route comparison;
- third strict Set-A material probe closure;
- broad V3-over-V2 wording;
- release readiness;
- all-app spend authorization.

It can be used for:

- confirming the K4 80,000-clique input identity gate;
- confirming the RT hardware gate;
- confirming the Embree same-contract control correctness on the serious row;
- proving that the next focused rerun, if any, must explicitly use the project
  venv path.

## Proposed Next Step, Not Authorized Yet

Ask 2-AI review whether one environment-corrected replacement run is allowed,
using the same script, same row, same success bars, same hard cap, and a new
output directory. The corrected command should use:

```text
PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python scripts/v3_phoenix_triangle_runner_m18_pod_ab.py ...
```

No such rerun is authorized by this report.

## Goal-Level Decision Audit

Decision: classify the consumed M18 POD attempt as failed environment intake
and seek 2-AI authorization before any environment-corrected rerun.

1. Was I foolish?
   Yes.
2. If yes, what actions made the decision foolish?
   I used the generic `python3` in the authorized POD command instead of first
   checking the historical project venv that earlier GPU/POD work used. That
   consumed the single focused authorization without testing the intended CuPy
   paths.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Before the paid run, run a zero-cost interpreter gate:
   `/root/rtdl_v3_rebuild_20260620/.venv/bin/python -c "import cupy, numba"`,
   and substitute the venv interpreter into the focused command before launch.
4. Can I now try a different path that actually solves the problem?
   Yes. Preserve the failed artifacts, document the failure honestly, then ask
   2-AI for a narrowly scoped replacement run using the verified venv. Do not
   rerun or claim performance until that authorization exists.
