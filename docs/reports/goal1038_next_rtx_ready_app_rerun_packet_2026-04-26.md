# Goal1038 Next RTX Ready-App Rerun Packet

Date: 2026-04-26

## Purpose

This packet defines the next paid RTX pod work after Goals 1033-1037. It is intentionally small and high-value: rerun only the four apps that currently have local CPU, Embree, and SciPy baseline-ready command surfaces.

Do not start a pod for a single app. If a pod is available, run this as one consolidated batch.

## Why This Packet Exists

Goal1036 fixed the `outlier_detection` `density_count` oracle path. The previous A5000 cloud artifact is still useful as RTX evidence, but it predates this local baseline correction. The next cloud session should refresh the RTX side for the four apps whose local same-command baselines now pass at `copies=20000`.

Local corrected baseline evidence:

- `docs/reports/goal1036_all_ready_apps_20000_after_outlier_fix_2026-04-26.md`
- all 12 CPU/Embree/SciPy rows passed at `copies=20000`.

## Target Apps

| App | RTX subpath | Local baseline status | Next RTX action |
|---|---|---|---|
| `outlier_detection` | `prepared_fixed_radius_density_summary` | CPU/Embree/SciPy pass at 20000 copies after Goal1036 | Rerun Group B and compare only scalar density-count semantics after review. |
| `dbscan_clustering` | `prepared_fixed_radius_core_flags` | CPU/Embree/SciPy pass at 20000 copies | Rerun Group B and compare only scalar core-count semantics after review. |
| `service_coverage_gaps` | `prepared_gap_summary` | CPU/Embree/SciPy pass at 20000 copies | Rerun prepared gap summary in Group D scope. |
| `event_hotspot_screening` | `prepared_count_summary` | CPU/Embree/SciPy pass at 20000 copies | Rerun prepared count summary in Group D scope. |

## Pod Requirements

Use one RTX-class NVIDIA GPU pod:

- RTX 4090, RTX A5000/A6000, L4, A10/A10G, or better.
- Do not use GTX 1070-class hardware for RT-core claims.
- Install `libgeos-dev` and `pkg-config` if graph or GEOS-gated groups are added later; this packet itself does not require graph.

## Bootstrap

```bash
cd /workspace/rtdl_python_only
export PYTHONPATH=src:.
export CUDA_PREFIX=/usr/local/cuda-12.4
export NVCC=/usr/local/cuda-12.4/bin/nvcc
export RTDL_NVCC=/usr/local/cuda-12.4/bin/nvcc
export RTDL_OPTIX_PTX_COMPILER=nvcc
export OPTIX_PREFIX=/workspace/vendor/optix-dev-9.0.0
export RTDL_OPTIX_LIB=/workspace/rtdl_python_only/build/librtdl_optix.so

PYTHONPATH=src:. python3 scripts/goal763_rtx_cloud_bootstrap_check.py \
  --output-json docs/reports/goal1038_bootstrap_check.json
```

Stop immediately if bootstrap status is not `ok`.

## Commands

Run fixed-radius scalar apps:

```bash
PYTHONPATH=src:. python3 scripts/goal761_rtx_cloud_run_all.py \
  --only prepared_fixed_radius_density_summary \
  --only prepared_fixed_radius_core_flags \
  --output-json docs/reports/goal1038_group_b_fixed_radius_refresh.json
```

Run mature prepared spatial summaries:

```bash
PYTHONPATH=src:. python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only prepared_gap_summary \
  --only prepared_count_summary \
  --output-json docs/reports/goal1038_group_d_spatial_ready_refresh.json
```

## Copy-Back Rule

Copy these artifacts back before stopping the pod:

- `docs/reports/goal1038_bootstrap_check.json`
- `docs/reports/goal1038_group_b_fixed_radius_refresh.json`
- `docs/reports/goal1038_group_d_spatial_ready_refresh.json`
- `docs/reports/goal759_outlier_dbscan_fixed_radius_rtx.json`
- `docs/reports/goal811_service_coverage_rtx.json`
- `docs/reports/goal811_event_hotspot_rtx.json`

## Claim Boundary

This packet collects refreshed RTX evidence only. It does not authorize public speedup claims, release authorization, or NVIDIA RT-core superiority wording.

Any comparison against Goal1036 local CPU/Embree/SciPy timings must be treated as internal planning evidence until reviewed for same hardware class, phase separation, repeated runs, correctness parity, and public wording compliance.
