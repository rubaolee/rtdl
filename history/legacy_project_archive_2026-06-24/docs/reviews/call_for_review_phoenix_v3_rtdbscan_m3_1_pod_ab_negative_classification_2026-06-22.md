# Call For Review: Phoenix V3 RTDBSCAN M3.1 Pod A/B Negative Classification

Please critically review the Phoenix V3 RTDBSCAN M3.1 focused pod A/B result
and the proposed classification.

Required verdict labels:

- `approve_release_ready`
- `approve_blocked_not_release`
- `changes_required`
- `reject`

This is not a release authorization request. A valid review must explicitly say
whether the M3.1 result can count as the second material Set-A runner-backed
probe. It must also explicitly say that V3 release, public speedup wording,
broad V3-over-V2 wording, true-zero-copy wording, and full all-app rerun remain
authorized or unauthorized.

## Files To Review

- `docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_1_pod_ab_2026-06-22.md`
- `docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_m3_1_pod_ab_20260622_191459/summary.json`
- `docs/handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md`
- `docs/reports/phoenix_v3_remaining_work_resource_plan_2026-06-22.md`
- `src/rtdsl/prepared_execution.py`
- `examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `scripts/v3_phoenix_rtdbscan_runner_m3_1_pod_ab.py`

## Proposed Codex Classification

```text
status: m3_1_rtdbscan_runner_backed_pod_ab_failed_material_set_a_not_release
evidence_valid: true
route_uses_productized_runner: true
signature_contract_preserved: true
same_pod_focused_result_collected: true
material_set_a_candidate: false
second_set_a_material_probe_obtained: false
all_app_rerun_authorized: false
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

## Key Evidence

```text
runner_metadata_present_all_runner_samples: true
all_claim_flags_false: true
signatures_stable: true
geomean_runner_vs_legacy_speedup: 0.5038091959795198
geomean_runner_vs_embree_speedup: 1.4917123537253953
material_set_a_candidate: false
```

The runner-backed route is faster than the Embree control, but the incumbent
comparison for this Set-A candidate is the existing OptiX grouped-stream Numba
column-signature route. Against that incumbent it is much slower:

```text
65,536 runner_vs_legacy_speedup: 0.381271446126756
262,144 runner_vs_legacy_speedup: 0.6657303749915396
```

Representative timing diagnosis:

```text
65,536 legacy elapsed_sec: 0.095091
65,536 legacy grouped_native_sec: 0.090146
65,536 runner elapsed_sec: 0.248945
65,536 runner prepared_runner_steady_state_sec: 0.090461
65,536 runner grouped_native_sec: 0.089911
65,536 runner adapter_non_native_estimated_sec: 0.153663

262,144 legacy elapsed_sec: 1.266585
262,144 legacy grouped_native_sec: 1.246784
262,144 runner elapsed_sec: 1.903061
262,144 runner prepared_runner_steady_state_sec: 1.248512
262,144 runner grouped_native_sec: 1.247843
262,144 runner adapter_non_native_estimated_sec: 0.633671
```

Codex hypothesis: the bottom-level native/partner execution is close to the
legacy path, but the current productized runner adds repeated Python-side
fingerprint/cache/report/metadata overhead inside the measured loop. This is a
generic runner overhead problem, not an RTDBSCAN-specific native-engine task.

## Review Questions

1. Is the proposed negative classification technically correct?
2. Can this result count as the second material Set-A runner-backed probe?
3. Is it correct to reject the `1.49x` runner-vs-Embree ratio as a success
   claim because the route loses to the incumbent OptiX legacy path?
4. Is the overhead diagnosis plausible from the cited timing evidence and code
   shape?
5. What exact next action is most responsible: bounded generic runner-overhead
   fix, switch to another Set-A route, or something else?
6. Are any release/public/all-app claims authorized by this packet?

## Required Non-Authorization Block

Please include an explicit block like:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
full_all_app_rerun_authorized_by_this_packet: false
```
