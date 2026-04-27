# Goal1039 Goal1038 Pod Artifact Audit

Date: 2026-04-27

## Scope

This audit checks the copied Goal1038 RTX pod artifacts against the accepted
Goal1038 rerun packet. It does not authorize public speedup claims or release.

## Required Artifacts

All required artifacts are present locally:

- `docs/reports/goal1038_bootstrap_check.json`
- `docs/reports/goal1038_group_b_fixed_radius_refresh.json`
- `docs/reports/goal1038_group_d_spatial_ready_refresh.json`
- `docs/reports/goal759_outlier_dbscan_fixed_radius_rtx.json`
- `docs/reports/goal811_service_coverage_rtx.json`
- `docs/reports/goal811_event_hotspot_rtx.json`
- `docs/reports/goal1038_rtx_cloud_batch_report_2026-04-26.md`

## Hardware

The copied report records:

- GPU: NVIDIA RTX A5000, 24564 MiB VRAM
- Driver: 580.126.09
- CUDA reported by `nvidia-smi`: 13.0
- NVCC toolkit: 12.4.131 at `/usr/local/cuda-12.4/bin/nvcc`
- OptiX SDK: `v9.0.0`

## Packet Scope Check

The executed groups match Goal1038's narrow scope:

| Group | Expected targets | Status |
|---|---|---|
| Group B | `prepared_fixed_radius_density_summary`, `prepared_fixed_radius_core_flags` | `ok`, `failed_count=0`, `entry_count=2` |
| Group D | `prepared_gap_summary`, `prepared_count_summary` | `ok`, `failed_count=0`, `entry_count=2` |

No broad A-H suite expansion is recorded in these copied group summaries.

## Per-App Evidence

| App | Artifact | Key RTX/OptiX timing | Correctness/status |
|---|---|---:|---|
| `outlier_detection` | `goal759_outlier_dbscan_fixed_radius_rtx.json` | prepared warm query median `0.000895502s` | `prepared_output.matches_oracle=true`; validation mode says `skipped`, oracle count omitted |
| `dbscan_clustering` | `goal759_outlier_dbscan_fixed_radius_rtx.json` | prepared warm query median `0.000825754s` | `prepared_output.matches_oracle=true`; validation mode says `skipped`, oracle count omitted |
| `service_coverage_gaps` | `goal811_service_coverage_rtx.json` | `optix_query=0.137949283s` | artifact generated successfully; compact result reports covered/uncovered counts |
| `event_hotspot_screening` | `goal811_event_hotspot_rtx.json` | `optix_query=0.213769975s` | artifact generated successfully; compact result reports hotspot count |

## Caveats

- The group summaries report `git_head` and `source_commit` as `fatal: not a git repository...`, because the pod directory was staged outside a git checkout. This repeats the traceability caveat seen in earlier cloud runs. The external report records the hardware/toolchain, but a future runner should inject a source commit marker into every copied group summary.
- The fixed-radius artifact was run with `skip_validation=true`. The output still reports `matches_oracle=true`, but oracle counts are null, so this audit treats it as refreshed RTX execution evidence, not final public correctness authorization.
- The Goal1038 packet intentionally does not authorize public speedup claims. This audit preserves that boundary.

## Verdict

Status: `evidence_collected_no_public_speedup_claim`.

The Goal1038 pod run successfully refreshed RTX/OptiX evidence for the four baseline-ready apps on RTX A5000 hardware. The copied artifacts satisfy the packet's scope and copy-back requirements.

Public speedup wording remains blocked until a separate review compares these artifacts against the corrected local CPU/Embree/SciPy baselines with same-semantics, phase-separated, repeated-run criteria.
