# Call For Review: Phoenix V3 RTDBSCAN M3.4 Pod A/B Parity Classification

Date: 2026-06-22
Requester: Codex
Scope: Phoenix V3 only. Do not discuss V4 / C ABI / embedding.

## Document Under Review

```text
docs/reports/phoenix_v3_rtdbscan_repeated_runner_route_m3_4_pod_ab_2026-06-22.md
```

## Evidence Under Review

```text
docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_m3_4_pod_ab_20260622_204719/summary.json
```

## Key Facts

```text
hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
dataset: clustered3d
point_counts: 65536, 262144
repeat: 7
warmup: 2
samples_per_variant_per_scale: 3

geomean_runner_vs_legacy_speedup: 0.997557675600175
geomean_runner_vs_embree_speedup: 2.941644953697829
legacy_parity_recovered: true
material_set_a_candidate: false
runner_metadata_present_all_runner_samples: true
runner_repeated_execution_all_runner_samples: true
all_claim_flags_false: true
```

The relevant incumbent is the legacy OptiX grouped-stream route, not Embree.

## Proposed Classification

```text
m3_4_rtdbscan_repeated_runner_parity_not_material_not_release
```

Proposed engineering action:

```text
Stop RTDBSCAN as the immediate second Set-A material-probe path.
Redirect to AABB runner generalization or productized typed continuation.
Do not authorize release, public speedup wording, broad V3-over-V2 wording, or full all-app pod rerun.
```

## Review Questions

Please return one of:

```text
approve_parity_classification_not_release
approve_with_required_edits_not_release
reject_classification
blocked_no_substantive_review
```

Answer explicitly:

1. Is `runner_vs_legacy = 0.9976x` correctly classified as parity, not material Set-A evidence?
2. Is it correct to ignore `runner_vs_embree = 2.94x` for material classification because legacy OptiX is the relevant incumbent?
3. Is the stop/redirect action correct under the prior threshold?
4. Are any report statements too strong or public-claim unsafe?
5. Does this result keep full all-app pod rerun unauthorized?

## Required Boundary

Do not authorize:

```text
release
public speedup claim
broad V3 faster than V2 claim
full all-app pod rerun
RTDBSCAN paper reproduction claim
V4 / C ABI / embedding work
```
