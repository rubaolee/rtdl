# Phoenix V3 M19 Triangle Environment-Corrected Focused POD Result

Date: 2026-06-22

Status: `focused_triangle_productized_runner_pod_accepted_third_strict_set_a_probe`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
third_strict_set_a_material_probe_closed: true
```

## Bottom Line

The one environment-corrected replacement focused Triangle POD run authorized
by Claude completed successfully on the RTX 4000 Ada pod. It used the verified
project venv, produced all three required variant payloads, matched the
`320000` triangle oracle on every variant, and passed all M17/M18 fail-closed
checks.

Claude result review accepted this as closing Triangle as the third strict
Set-A material runtime-trunk probe. This remains focused productized-runtime
evidence only. It is not release
authorization, broad V3-over-V2 proof, public speedup wording, or all-app POD
authorization.

Result review:

```text
docs/reviews/claude_phoenix_v3_m19_triangle_env_corrected_pod_result_review_2026-06-22.md
verdict: accept_m19_triangle_third_strict_set_a_probe
```

Codex + Claude result consensus:

```text
docs/reviews/codex_claude_phoenix_v3_m19_triangle_result_2ai_consensus_2026-06-22.md
status: accept_m19_triangle_third_strict_set_a_probe
```

## Authorization And Pre-Launch Gate

External review:

```text
docs/reviews/claude_phoenix_v3_m19_triangle_env_corrected_rerun_review_2026-06-22.md
verdict: authorize_m19_one_env_corrected_triangle_replacement_pod
```

Codex + Claude consensus:

```text
docs/reviews/codex_claude_phoenix_v3_m19_triangle_env_corrected_rerun_2ai_consensus_2026-06-22.md
status: authorize_one_env_corrected_triangle_replacement_pod_after_prelaunch_check
```

Required pre-launch subprocess interpreter check:

```text
status: pass
subprocess command construction uses sys.executable
no hardcoded /usr/bin/python3 or bare python3 in command construction except the script shebang
```

## Command

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

Exit code:

```text
0
```

Copied local evidence:

```text
docs/rebuild/v3/evidence/phoenix_v3_triangle_runner_m18_focused_pod_ab_venv_20260622/
docs/rebuild/v3/evidence/phoenix_v3_triangle_runner_m18_focused_pod_ab_venv_20260622.run.log
docs/rebuild/v3/evidence/phoenix_v3_triangle_runner_m18_focused_pod_ab_venv_20260622.exit_code
```

## Input And Hardware Gates

```text
cliques: 80000
edge_count: 480000
oracle_triangle_count: 320000
edge_file_preflight_status: pass
edge_file_sha256: 8bc1bd3fc75d86707d326fc4e2913cae7d6c380c5afa788f08b5bdbb18127005
edge_file_generated_now: true
gpu: NVIDIA RTX 4000 Ada Generation
driver: 550.127.05
compute_cap: 8.9
rt_hardware_gate_status: pass
```

## Correctness And Runtime Path

```text
failed_check_count: 0
variant_count: 3
all_variant_oracle_checks_passed: true
```

Oracle checks:

```text
embree_same_contract_control: observed=320000, expected=320000, pass
legacy_app_front_door_optix: observed=320000, expected=320000, pass
productized_prepared_execution_runner: observed=320000, expected=320000, pass
```

Runner path:

```text
productized_execution_path: prepared_execution_session_runner
runtime_executed: true
runtime_trunk_executes_end_to_end: true
validation_passed: true
internal_device_residency_between_rtdl_phases: true
hot_path_host_materialization: false
weighted_hit_sum: 320000
```

## Timings

```text
Embree same-contract control:
  query_median_ms: 549.2332428693771
  wrapper_wall_sec: 11.425547204911709

Legacy app-front-door OptiX:
  query_median_ms: 1.583486795425415
  wrapper_wall_sec: 1.8036402389407158

Productized prepared-execution runner:
  runner_measured_median_sec: 0.0002274438738822937
  runner_outer_wall_sec: 0.8520944193005562
  runner_prepare_or_cache_sec: 0.3262270614504814
```

Computed comparisons:

```text
runner_vs_embree_hot_speedup: 2414.807809480132x
runner_vs_embree_wall_speedup: 13.408780700958467x
runner_vs_legacy_hot_speedup: 6.962099125364431x
runner_vs_legacy_wall_speedup: 2.1167140613609914x
legacy_vs_embree_hot_speedup: 346.85053544877945x
legacy_vs_embree_wall_speedup: 6.334715182237214x
```

## Bar Check

```text
all variants match oracle_triangle_count=320000: pass
runtime_executed=true: pass
productized_execution_path=prepared_execution_session_runner: pass
runtime_trunk_executes_end_to_end=true: pass
runner_vs_embree_hot_speedup >= 1.20x: pass
runner_vs_embree_wall_speedup >= 1.20x: pass
runner_vs_legacy_wall_speedup >= 0.98x: pass
claim flags remain false: pass
```

Accepted interpretation after result review:

```text
M19 focused Triangle result passes the M17/M18/M19 strict focused success bars.
Triangle is closed as the third strict Set-A material runtime-trunk probe.
No additional focused Triangle rerun is authorized.
```

## Claim Boundary

This result may support:

- focused Triangle evidence for a reusable RTDL productized runner path;
- the third strict Set-A material runtime-trunk probe closure;
- proof that the wrong-interpreter M18 attempt was an environment failure and
  that the intended venv route can run.

This result does not support:

- V3 release;
- public speedup wording;
- broad V3-over-V2 wording;
- all-app POD spend;
- true zero-copy;
- V4, C ABI, embedding, or external buffer interop claims;
- a claim that all benchmark apps are fast.

## Goal-Level Decision Audit

Decision: accept the M19 environment-corrected focused POD result as the third
strict Set-A material runtime-trunk probe after Claude result review.

1. Was I foolish?
   No; the data passes the pre-registered focused bars and external result
   review accepted the interpretation.
2. If yes, what actions made the decision foolish?
   It would be foolish to expand this focused result into release, all-app, or
   broad V3-over-V2 claims. This report explicitly forbids that.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Ignore the result because attempt 1 failed. That would be wrong because
   M19 was externally authorized specifically to correct the environment and
   measure the intended path.
4. Can I now try a different path that actually solves the problem?
   Yes. Record Triangle as closed, stop Triangle reruns, and move to the next
   Phoenix V3 gate under the Set-A/Set-B scorecard.
