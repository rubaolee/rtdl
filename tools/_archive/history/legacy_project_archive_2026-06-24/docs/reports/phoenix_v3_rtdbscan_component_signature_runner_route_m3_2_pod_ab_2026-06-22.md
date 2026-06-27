# Phoenix V3 RTDBSCAN Component-Signature Runner M3.2 Pod A/B

Date: 2026-06-22
Status: `m3_2_rtdbscan_runner_parity_recovered_not_material_set_a_not_release`

## Summary

M3.2 reran the same focused RTDBSCAN component-signature A/B after the generic
runner fingerprint/overhead fix.

Result:

```text
geomean_runner_vs_legacy_speedup: 0.9929975216946967
geomean_runner_vs_embree_speedup: 2.934280113671061
legacy_parity_recovered: true
material_vs_incumbent_legacy_candidate: false
material_set_a_candidate: false
second_set_a_material_probe_obtained: false
runner_metadata_present_all_runner_samples: true
all_claim_flags_false: true
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
full_all_app_rerun_authorized_by_this_packet: false
```

This is a real fix and a successful parity recovery, but it is not the second
material Set-A win. The runner is now roughly equal to the incumbent legacy
OptiX route, not materially faster than it.

## Evidence

```text
remote_run_dir: /root/rtdl_v3_rebuild_20260620/phoenix_v3_rtdbscan_m3_2_pod_ab_20260622_193805
local_evidence_dir: docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_m3_2_pod_ab_20260622_193805
raw_summary: docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_m3_2_pod_ab_20260622_193805/summary.json
corrected_classification: docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_m3_2_pod_ab_20260622_193805/classification_corrected.json
dataset: clustered3d
point_counts: 65536, 262144
repeat: 7
warmup: 2
samples_per_variant_per_scale: 3
hardware: NVIDIA RTX 4000 Ada Generation
```

Median payload times:

| point_count | variant | median payload sec | ratio |
| --- | --- | ---: | --- |
| 65,536 | legacy OptiX grouped-stream Numba signature | 0.095439 | incumbent |
| 65,536 | runner-backed OptiX grouped-stream Numba signature | 0.096160 | `0.992x` vs legacy |
| 65,536 | Embree core-flags Numba prepared-grid signature | 0.389723 | runner is `4.053x` faster |
| 262,144 | legacy OptiX grouped-stream Numba signature | 1.262815 | incumbent |
| 262,144 | runner-backed OptiX grouped-stream Numba signature | 1.271078 | `0.993x` vs legacy |
| 262,144 | Embree core-flags Numba prepared-grid signature | 2.700315 | runner is `2.124x` faster |

## Comparison To M3.1

M3.1 before the fix:

```text
geomean_runner_vs_legacy_speedup: 0.5038091959795198
65,536 runner median: 0.249405 sec
262,144 runner median: 1.902552 sec
```

M3.2 after the fix:

```text
geomean_runner_vs_legacy_speedup: 0.9929975216946967
65,536 runner median: 0.096160 sec
262,144 runner median: 1.271078 sec
```

The fix recovered the runner route from a roughly 2x loss to near parity with
the incumbent OptiX route.

Representative runner timing confirms the overhead moved out of the hot path:

```text
65,536 elapsed_sec: 0.096066
65,536 grouped_native_sec: 0.090424
65,536 adapter_non_native_estimated_sec: 0.000048

262,144 elapsed_sec: 1.271289
262,144 grouped_native_sec: 1.249297
262,144 adapter_non_native_estimated_sec: 0.000965
```

## Classification Correction

The raw `summary.json` was produced by the earlier script logic and still marks
`material_set_a_candidate: true` because the old gate required:

```text
runner_vs_embree_geomean >= 1.15
runner_vs_legacy_geomean >= 0.98
```

That gate is too broad for the current Phoenix release discipline. The
corrected classification in `classification_corrected.json` supersedes that
raw field:

```text
legacy_parity_recovered: true
material_vs_incumbent_legacy_candidate: false
material_set_a_candidate: false
second_set_a_material_probe_obtained: false
```

Reason: Phoenix needs material speed from the productized path against the
decision-relevant incumbent. `0.993x` versus the legacy OptiX path is parity
recovery, not material superiority.

The runner script has been updated locally so future runs separate:

- `legacy_parity_recovered`;
- `material_vs_incumbent_legacy_candidate`; and
- `material_set_a_candidate`.

## Boundaries

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
full_all_app_rerun_authorized_by_this_packet: false
```

No all-app rerun is authorized by M3.2. AABB M2.1 remains the only current
material focused Set-A runner-backed result.

## Next

Two responsible choices remain:

1. implement a true repeated prepared-session execution API that removes more
   generic runner/report overhead and then rerun M3.2; or
2. switch to another Set-A route, because RTDBSCAN runner parity is now
   recovered but not winning.

Do not spend more RTDBSCAN time unless the next change is generic runner work,
not app-specific DBSCAN logic.

## Goal-Level Decision Audit

Decision: classify M3.2 as successful runner parity recovery, not material
Set-A evidence.

1. Was I foolish?
   No for this decision.
2. What actions would have made this foolish?
   It would be foolish to reuse the raw script's old `material_set_a_candidate:
   true` field as a second Set-A win while ignoring `0.993x` versus the
   incumbent OptiX route.
3. Was there another path?
   Yes. I could have declared success because runner-vs-Embree is `2.934x`,
   but that would be the same misleading comparison pattern already rejected.
4. Can I now try a different path that truly solves the problem?
   Yes. Either build the repeated prepared-session runner to seek a real
   productized-path win, or move to another Set-A route with M3.2 recorded as
   parity recovery.
