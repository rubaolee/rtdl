# Phoenix V3 RTDBSCAN Component-Signature Runner M3.1 Pod A/B

Date: 2026-06-22
Status: `m3_1_rtdbscan_runner_backed_pod_ab_failed_material_set_a_not_release`

## Summary

The RTDBSCAN grouped-stream Numba column-signature route was measured on the
same RTX 4000 Ada pod after being wired through the productized Phoenix V3
`prepared_execution_session_runner`.

The evidence is valid but the performance result is negative:

```text
runner_metadata_present_all_runner_samples: true
all_claim_flags_false: true
signatures_stable: true
geomean_runner_vs_legacy_speedup: 0.5038091959795198
geomean_runner_vs_embree_speedup: 1.4917123537253953
material_set_a_candidate: false
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
full_all_app_rerun_authorized_by_this_packet: false
```

This does not count as the second material Set-A runner-backed probe. The
runner beats the Embree control, but the relevant incumbent for this route is
the existing OptiX grouped-stream Numba column-signature path, and the runner
is substantially slower than that legacy path.

## Evidence

```text
remote_run_dir: /root/rtdl_v3_rebuild_20260620/phoenix_v3_rtdbscan_m3_1_pod_ab_20260622_191459
local_evidence_dir: docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_m3_1_pod_ab_20260622_191459
summary: docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_m3_1_pod_ab_20260622_191459/summary.json
pod: root@213.173.108.14 -p 11592
hardware: NVIDIA RTX 4000 Ada Generation
dataset: clustered3d
point_counts: 65536, 262144
repeat: 7
warmup: 2
samples_per_variant_per_scale: 3
```

Measured median payload times:

| point_count | variant | median payload sec | interpretation |
| --- | ---: | ---: | --- |
| 65,536 | legacy OptiX grouped-stream Numba signature | 0.095091 | incumbent fast path |
| 65,536 | runner-backed OptiX grouped-stream Numba signature | 0.249405 | runner visible but slower |
| 65,536 | Embree core-flags Numba prepared-grid signature | 0.390065 | slower control |
| 262,144 | legacy OptiX grouped-stream Numba signature | 1.266585 | incumbent fast path |
| 262,144 | runner-backed OptiX grouped-stream Numba signature | 1.902552 | runner visible but slower |
| 262,144 | Embree core-flags Numba prepared-grid signature | 2.706919 | slower control |

Scale ratios:

```text
65,536 runner_vs_legacy_speedup: 0.381271446126756
65,536 runner_vs_embree_speedup: 1.5639811838094677
262,144 runner_vs_legacy_speedup: 0.6657303749915396
262,144 runner_vs_embree_speedup: 1.4227833718774562
```

## Failure Diagnosis

The bottom-level native/partner execution appears close to the legacy route.
The loss is in the productized runner wrapper path.

Representative sample, 65,536 points:

```text
legacy elapsed_sec: 0.095091
legacy adapter_run_sec: 0.090198
legacy grouped_native_sec: 0.090146

runner elapsed_sec: 0.248945
runner adapter_run_sec: 0.243574
runner prepared_runner_steady_state_sec: 0.090461
runner grouped_native_sec: 0.089911
runner adapter_non_native_estimated_sec: 0.153663
```

Representative sample, 262,144 points:

```text
legacy elapsed_sec: 1.266585
legacy adapter_run_sec: 1.247253
legacy grouped_native_sec: 1.246784

runner elapsed_sec: 1.903061
runner adapter_run_sec: 1.881514
runner prepared_runner_steady_state_sec: 1.248512
runner grouped_native_sec: 1.247843
runner adapter_non_native_estimated_sec: 0.633671
```

Current hypothesis: `run_radius_graph_component_signature_3d_prepared_session`
does too much Python-side runner work inside the measured loop, including
rebuilding tuple/fingerprint/cache/report metadata for large point sets on each
iteration. The old path prepares once and then reuses the prepared continuation
inside the loop. This is a generic runner overhead problem, not an RTDBSCAN
native-engine opportunity.

Claude review accepted this diagnosis and added a correctness warning:
`_stable_input_fingerprint` currently uses truncated sequence reprs, shaped as
`repr(tuple(value))[:2048]`, for large sequences. That is both O(N) work in the
hot path and collision-prone for prepared-session cache keys. Any speed fix
must also fix the cache-key correctness issue.

## Classification

```text
evidence_valid: true
route_uses_productized_runner: true
signature_contract_preserved: true
same_pod_focused_result_collected: true
material_set_a_candidate: false
second_set_a_material_probe_obtained: false
all_app_rerun_authorized: false
release_authorized: false
```

Do not use the `1.49x` runner-vs-Embree ratio as a success claim. It is useful
only as a control showing that the OptiX route still beats an Embree route. The
decision-relevant comparison for Phoenix Gap 1 is runner-backed OptiX against
the existing legacy OptiX grouped-stream path, where the runner is much slower.

## Next Controlled Work

1. Do not count RTDBSCAN M3.1 as the second material Set-A win.
2. Fix runner overhead generically, if a small bounded change can avoid
   repeated large input fingerprinting/report construction in the measured
   loop while preserving explicit backend/partner/cache metadata. The fix must
   also replace collision-prone truncated sequence reprs in cache keys.
3. If the generic runner overhead fix is not small, shift to the next Set-A
   candidate before spending more pod time.
4. Keep full all-app V2.14 vs Phoenix V3 rerun unauthorized until at least two
   productized-path Set-A focused probes are material and externally reviewed.

## Goal-Level Decision Audit

Decision: classify the M3.1 RTDBSCAN runner-backed pod A/B as valid evidence
but not a material Set-A candidate.

1. Was I foolish?
   No for this decision.
2. What actions would have made this foolish?
   It would be foolish to cite the `1.49x` runner-vs-Embree geomean while
   hiding that the same runner is `0.50x` versus the incumbent OptiX legacy
   route.
3. Was there another path?
   Yes. I could have stopped at "runner metadata present" or treated Embree as
   the only comparison. That would have repeated the old mistake of turning a
   narrow positive number into a broad V3 claim.
4. Can I now try a different path that truly solves the problem?
   Yes. The different path is to attack generic runner overhead, not
   RTDBSCAN-specific app logic, and to require another focused pod A/B before
   any all-app rerun.
