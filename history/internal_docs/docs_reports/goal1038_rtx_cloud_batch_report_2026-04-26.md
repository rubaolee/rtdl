# Goal1038 RTX Cloud Batch Report

Date: 2026-04-26
Execution Mode: `rsync` push to clean Pod + ssh inline execution

## Hardware Metadata

- **GPU**: NVIDIA RTX A5000, 24564 MiB VRAM
- **Driver Version**: 580.126.09
- **CUDA Version**: 13.0
- **NVCC Toolkit**: `nvcc` 12.4.131 (`/usr/local/cuda-12.4/bin/nvcc`)
- **OptiX SDK**: `v9.0.0` (Cloned directly from NVIDIA/optix-dev repository to `/workspace/vendor/optix-dev-9.0.0`)

## Exact Commands

```bash
# 1. Bootstrap and compilation check
python3 scripts/goal763_rtx_cloud_bootstrap_check.py \
  --output-json docs/reports/goal1038_bootstrap_check.json

# 2. Group B (Fixed Radius Summary)
python3 scripts/goal761_rtx_cloud_run_all.py \
  --only prepared_fixed_radius_density_summary \
  --only prepared_fixed_radius_core_flags \
  --output-json docs/reports/goal1038_group_b_fixed_radius_refresh.json

# 3. Group D (Spatial Summary)
python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only prepared_gap_summary \
  --only prepared_count_summary \
  --output-json docs/reports/goal1038_group_d_spatial_ready_refresh.json
```

## Pass/Fail Status

| Phase | Status | Failures | Notes |
|---|---|---|---|
| **Bootstrap Check** (`goal763`) | **PASS** (`ok`) | 0 | OptiX `librtdl_optix.so` successfully compiled and linked natively on RTX hardware. |
| **Group B Refresh** (`goal761`) | **PASS** (`ok`) | 0 | `outlier_detection` and `dbscan_clustering` ran 20,000 copies successfully against the freshly fixed Goal1036 baseline oracle definitions. |
| **Group D Refresh** (`goal761`) | **PASS** (`ok`) | 0 | `service_coverage_gaps` and `event_hotspot_screening` generated outputs successfully. |

## Artifact Paths

All explicitly and implicitly generated artifacts were successfully copied back to the local host via `scp`:

- `docs/reports/goal1038_bootstrap_check.json`
- `docs/reports/goal1038_group_b_fixed_radius_refresh.json`
- `docs/reports/goal1038_group_d_spatial_ready_refresh.json`
- `docs/reports/goal759_outlier_dbscan_fixed_radius_rtx.json`
- `docs/reports/goal811_service_coverage_rtx.json`
- `docs/reports/goal811_event_hotspot_rtx.json`

## Verdict and Claim Boundaries

Status: `evidence_collected_no_public_speedup_claim`.

All targeted baseline-ready apps successfully generated cloud performance evidence on real RTX-class hardware. However, this report **DOES NOT** authorize public RTX speedup or release claims. These artifacts are strictly internal evidence representing the OptiX subpath timing (e.g., *prepared fixed-radius scalar threshold-count*). They must undergo phase-separated semantic review against their matching CPU/Embree baselines prior to any external marketing or performance documentation.
