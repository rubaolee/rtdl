# Call For Review: Phoenix V3 M19 Triangle Environment-Corrected POD Result

Date: 2026-06-22

Status: `request_m19_result_interpretation_review`

This review asks whether the M19 focused Triangle POD result can close Triangle
as the third strict Set-A material runtime-trunk probe. It does not ask for
release authorization, public speedup wording, broad V3-over-V2 wording, or
all-app POD spend.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
third_strict_set_a_material_probe_closed: review_requested
```

## Packet

- Result report:
  `docs/reports/phoenix_v3_m19_triangle_env_corrected_pod_result_2026-06-22.md`
- Summary JSON:
  `docs/rebuild/v3/evidence/phoenix_v3_triangle_runner_m18_focused_pod_ab_venv_20260622/summary.json`
- Run log:
  `docs/rebuild/v3/evidence/phoenix_v3_triangle_runner_m18_focused_pod_ab_venv_20260622.run.log`
- M19 authorization review:
  `docs/reviews/claude_phoenix_v3_m19_triangle_env_corrected_rerun_review_2026-06-22.md`
- Codex + Claude authorization consensus:
  `docs/reviews/codex_claude_phoenix_v3_m19_triangle_env_corrected_rerun_2ai_consensus_2026-06-22.md`
- M18/M19 control JSON:
  `docs/rebuild/v3/phoenix_v3_m18_triangle_runner_harness_2026-06-22.json`
- Handoff:
  `docs/handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md`

## Result Facts

```text
exit_code: 0
failed_check_count: 0
variant_count: 3
all_variant_oracle_checks_passed: true
edge_file_preflight_status: pass
edge_file_sha256: 8bc1bd3fc75d86707d326fc4e2913cae7d6c380c5afa788f08b5bdbb18127005
rt_hardware_gate_status: pass
gpu: NVIDIA RTX 4000 Ada Generation, driver 550.127.05, compute_cap 8.9
```

Oracle:

```text
embree_same_contract_control: observed=320000, expected=320000, pass
legacy_app_front_door_optix: observed=320000, expected=320000, pass
productized_prepared_execution_runner: observed=320000, expected=320000, pass
```

Productized runtime path:

```text
productized_execution_path: prepared_execution_session_runner
runtime_executed: true
runtime_trunk_executes_end_to_end: true
validation_passed: true
internal_device_residency_between_rtdl_phases: true
hot_path_host_materialization: false
weighted_hit_sum: 320000
```

Timings:

```text
Embree query_median_ms: 549.2332428693771
Embree wrapper_wall_sec: 11.425547204911709
Legacy OptiX query_median_ms: 1.583486795425415
Legacy OptiX wrapper_wall_sec: 1.8036402389407158
Runner measured_median_sec: 0.0002274438738822937
Runner outer_wall_sec: 0.8520944193005562
Runner prepare_or_cache_sec: 0.3262270614504814
```

Comparisons:

```text
runner_vs_embree_hot_speedup: 2414.807809480132x
runner_vs_embree_wall_speedup: 13.408780700958467x
runner_vs_legacy_hot_speedup: 6.962099125364431x
runner_vs_legacy_wall_speedup: 2.1167140613609914x
legacy_vs_embree_hot_speedup: 346.85053544877945x
legacy_vs_embree_wall_speedup: 6.334715182237214x
```

Pre-registered focused bars:

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

## Requested Verdict Labels

Choose exactly one:

- `accept_m19_triangle_third_strict_set_a_probe`: the focused result satisfies
  the M17/M18/M19 bars and Triangle may be recorded as the third strict Set-A
  material runtime-trunk probe, with all release/public/all-app/broad claims
  still blocked.
- `accept_m19_result_but_do_not_close_probe`: the run is valid focused
  evidence, but Triangle should not close the third strict Set-A probe; explain
  why.
- `revise_m19_result_interpretation`: require specific edits or additional
  local analysis before deciding.
- `reject_m19_result`: the run is invalid or cannot be used.

Regardless of verdict, explicitly state:

- release authorization: yes/no
- public speedup authorization: yes/no
- broad V3-over-V2 authorization: yes/no
- all-app POD authorization: yes/no
- whether another focused Triangle rerun is authorized: yes/no
- whether M19 can be cited as broad V3 performance: yes/no
- whether Triangle closes the third strict Set-A material probe: yes/no

## Goal-Level Decision Audit

Decision: seek result review before closing the third strict Set-A material
probe.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   It would be foolish to convert a focused pass into release/all-app/broad
   performance wording. This review forbids that.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Declare the probe closed without review. That would skip the user's
   2-AI consensus rule for important results.
4. Can I now try a different path that actually solves the problem?
   Yes. Ask for a strict result verdict, then update Set-A status according to
   the review.
