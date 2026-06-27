I have now read all packet documents, the raw `summary.json`, the run log, the pre-run authorization review, and the 2AI consensus. I am writing the review from evidence only.

---

# External Critical Review: Phoenix V3 M19 Triangle Environment-Corrected POD Result

**Date:** 2026-06-23
**Reviewer role:** External critical reviewer (not a member of the production team)
**Scope:** Strict result verdict only — whether the M19 focused Triangle POD result closes Triangle as the third strict Set-A material runtime-trunk probe. This is not a release review, not an all-app spend review, and not a broad V3-over-V2 review.

---

## Verdict

```
accept_m19_triangle_third_strict_set_a_probe
```

---

## Explicit Authorization Answers

| Item | Answer |
|---|---|
| Release authorization | **No** |
| Public speedup authorization | **No** |
| Broad V3-over-V2 authorization | **No** |
| All-app POD authorization | **No** |
| Another focused Triangle rerun authorized | **No** — probe is closed; no improvement run is needed or permitted |
| M19 may be cited as broad V3 performance | **No** |
| Triangle closes the third strict Set-A material probe | **Yes** |

---

## Authorization Chain Verification

The pre-run chain is complete and traceable:

1. **M17 consensus**: `accept_m17_authorize_m18_runner_harness_no_pod` — harness authorized without POD spend
2. **M18 harness initial + second + final reviews**: three-round external review; both blocking issues (hot-path scalar materialization, control oracle and edge-checksum fail-closed) were remediated and regression-tested before final POD authorization was issued
3. **M18 attempt 1**: consumed the M18 authorization; failed with `ModuleNotFoundError: No module named 'cupy'` on the `/usr/bin/python3` interpreter; `failed_check_count: 6`; no performance evidence produced; correctly classified as an environment/intake failure
4. **M19 external review**: `authorize_m19_one_env_corrected_triangle_replacement_pod` — authorized exactly one replacement run, with a required zero-cost subprocess-interpreter pre-launch check
5. **Codex + Claude 2AI consensus**: accepted the M19 external verdict; Codex independently confirmed via `rg` that all subprocess command construction uses `sys.executable` — pre-launch check passed
6. **M19 run**: executed exactly once using the authorized command and the verified project venv; new output directory; attempt 1 artifacts not overwritten
7. **Result review**: requested before closing the probe — this review

The chain satisfies the project's 2-AI consensus rule for important results. No step was skipped.

---

## Command Verification

The authorized command (from the 2AI consensus) and the command recorded in the result report match exactly in every token:

```
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

No token differs. The interpreter is the project venv, not `/usr/bin/python3`. This is the corrected path and is the sole change from attempt 1.

---

## Evidence Verification

I read `summary.json` directly and cross-checked every value in the call-for-review packet against the raw file.

**Edge file identity:**

| Field | Expected | Actual | Match |
|---|---|---|---|
| SHA256 | `8bc1bd3fc75d86707d326fc4e2913cae7d6c380c5afa788f08b5bdbb18127005` | `8bc1bd3fc75d86707d326fc4e2913cae7d6c380c5afa788f08b5bdbb18127005` | ✓ |
| Edge count | 480,000 | 480,000 | ✓ |
| Bytes | 3,840,000 | 3,840,000 | ✓ |
| `generated_now` | required | `true` | ✓ |
| Preflight status | pass | pass | ✓ |

The edge file SHA matches attempt 1's SHA — correct, because the K4 80,000-clique ladder is a deterministic construction.

**Hardware gate:**

| Field | Value | Status |
|---|---|---|
| GPU | NVIDIA RTX 4000 Ada Generation | ✓ |
| Driver | 550.127.05 | ✓ |
| compute_cap | 8.9 | ✓ |
| `optix_capable_gpu_present` | true | ✓ |
| `rt_hardware_gate_status` | pass | ✓ |

**Run outcome:**

| Field | Value | Status |
|---|---|---|
| exit_code | 0 | ✓ |
| variant_count | 3 | ✓ |
| failed_check_count | 0 | ✓ |
| all_variant_oracle_checks_passed | true | ✓ |

**Oracle checks — all three variants:**

| Variant | Observed | Expected | Pass |
|---|---|---|---|
| `embree_same_contract_control` | 320,000 | 320,000 | ✓ |
| `legacy_app_front_door_optix` | 320,000 | 320,000 | ✓ |
| `productized_prepared_execution_runner` | 320,000 | 320,000 | ✓ |

**Productized runner path metadata:**

| Field | Value | Required | Pass |
|---|---|---|---|
| `productized_execution_path` | `prepared_execution_session_runner` | `prepared_execution_session_runner` | ✓ |
| `runtime_executed` | true | true | ✓ |
| `runtime_trunk_executes_end_to_end` | true | true | ✓ |
| `validation_passed` | true | true | ✓ |
| `hot_path_host_materialization` | false | false | ✓ |
| `internal_device_residency_between_rtdl_phases` | true | V3 boundary holds | ✓ |

The scalar `weighted_hit_sum` finalization happens once after measured repeats, confirmed by `measured_output_finalized_once: true`, `per_repeat_output_finalization_avoided: true`, `output_finalize_sec: 7.89e-5`. This is the correct implementation of the hot-path boundary fix from the second M18 harness revision.

**Repeat requirement:**

| Field | Value | Required |
|---|---|---|
| `measured_repeat_count` | 5 | 5 |
| `material_probe_repeat_requirement_met` | true | true |

Individual repeat timings (seconds): `[0.000253, 0.000241, 0.000221, 0.000219, 0.000227]`. Spread ratio best-to-worst is ~1.15x. Variance is small and consistent with warm GPU execution. The median (0.0002274s) is reliable.

**Pre-registered bar checks:**

| Bar | Observed | Required | Pass |
|---|---|---|---|
| All variants oracle 320,000 | 320,000 ✓ | 320,000 | ✓ |
| `runtime_executed=true` | true | true | ✓ |
| `productized_execution_path=prepared_execution_session_runner` | match | exact | ✓ |
| `runtime_trunk_executes_end_to_end=true` | true | true | ✓ |
| `runner_vs_embree_hot_speedup >= 1.20x` | **2414.8x** | ≥1.20x | ✓ |
| `runner_vs_embree_wall_speedup >= 1.20x` | **13.4x** | ≥1.20x | ✓ |
| `runner_vs_legacy_wall_speedup >= 0.98x` | **2.12x** | ≥0.98x | ✓ |
| Claim flags remain false | confirmed | all false | ✓ |

No bar is borderline. All pass with substantial margins. The hot-speedup figure (2414x) is dominated by the Embree query median (~549ms) versus the runner measured median (~0.227ms). This ratio is architecturally expected: Embree runs on CPU and does not use RT cores; the productized runner uses OptiX device-resident execution with cupy tensor handoff.

**Static harness fields (`third_strict_set_a_material_probe_closed: false`, `status: "triangle_runner_m18_harness_ready_not_pod_authorized"`) in summary.json:**

These are harness design-time constants, not post-run assessments. They were set when the harness was built to record the state before the run. The run log confirms exit code 0 and all bar checks passed. These static fields do not invalidate the result; they reflect the pre-run state and require this review to update the probe status.

---

## Scope Check

This result is evidence only for what was measured:

- The K4 80,000-clique Triangle input on the RTX 4000 Ada, with the project venv, using the authorized harness, in one run, on 2026-06-22.
- The productized `prepared_execution_session_runner` path executes correctly end-to-end for this input on this hardware.

It is not evidence for any other input size, any other app, any other hardware, the full all-app paired suite, or any V2-vs-V3 comparison across the release surface.

---

## Relationship to the Existing 2/2 Probe Precondition

The scorecard frozen before M19 records `Focused material productized probes: 2 / 2 required` as already closed. Triangle (M19) would be the third corroborating probe against a precondition that required two. Adding it:

- Provides additional depth that a third distinct Set-A app confirms the productized runner path end-to-end on GPU
- Does **not** change the release gate status (release remains blocked for other reasons: Set-A severe regression below 0.90x, Set-A app-win shortfall, Set-B parity row, lack of broad V2.x paired evidence)
- Does **not** change the all-app POD authorization status
- Does **not** change any public wording authorization

The third probe is additional corroborating evidence. Accepting it does not lower any bar; it records an accurate factual state.

---

## What This Result Does and Does Not Support

**May be recorded as:**
- Triangle (K4 80,000-clique) is a passed strict Set-A material runtime-trunk probe for the `prepared_execution_session_runner` productized path
- Third focused material probe on a distinct Set-A app, in addition to the two probes already closed
- Confirmation that the wrong-interpreter M18 attempt was purely an environment failure: the intended venv path runs correctly on the same hardware with the same harness

**Expressly not supported:**
- V3 release authorization
- Public speedup wording of any kind
- Broad V3-over-V2 performance wording
- All-app POD spend authorization
- True zero-copy claims
- V4, C ABI, embedding, or external buffer interop claims
- A claim that all benchmark apps are fast or that V3 beats V2 in general
- Any improvement rerun or follow-up triangle focused run

---

## Next Action

Record `third_strict_set_a_material_probe_closed: true` for Triangle in the M18/M19 control JSON and the probe inventory. No additional focused Triangle runs are authorized, needed, or permitted. The probe is closed.

Update the control JSON status field from `m19_env_corrected_triangle_focused_pod_pass_result_review_required` to `m19_env_corrected_triangle_focused_pod_accepted_third_strict_set_a_probe`.

No release action. No public wording action. No all-app spend action.
