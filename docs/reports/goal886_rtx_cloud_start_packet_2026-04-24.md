# Goal886 RTX Cloud Start Packet

Date: 2026-04-24

## Start Decision

Cloud can start now if an RTX-class GPU is available.

Local current-head checks passed at commit:

```text
7815c536850c073654aabb5224af783645f7a9f2
```

Readiness result:

```text
goal824_pre_cloud_rtx_readiness_gate: valid=true
active_runner_dry_run: status=ok, entry_count=5, unique_command_count=4
deferred_runner_dry_run: status=ok, entry_count=15, unique_command_count=14
one-shot active dry-run: status=ok
one-shot deferred dry-run: status=ok, include_deferred=true, only_count=12
```

## Pod Requirement

Use an RTX-class NVIDIA GPU with real RT cores, for example RTX 4090, RTX
A5000/A6000, L4, or A10/A10G. Do not use GTX 1070-class hardware for RT-core
claim evidence.

## Command 1: Active Evidence Batch

Run this first:

```bash
cd /workspace/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal769_rtx_pod_one_shot.py \
  --branch codex/rtx-cloud-run-2026-04-22 \
  --optix-prefix /workspace/vendor/optix-dev-9.0.0 \
  --output-json docs/reports/goal769_rtx_pod_one_shot_summary_latest.json \
  --artifact-json docs/reports/goal762_rtx_cloud_artifact_report_latest.json \
  --artifact-md docs/reports/goal762_rtx_cloud_artifact_report_latest.md \
  --bundle-tgz docs/reports/goal769_rtx_pod_artifacts_latest.tgz
```

This active batch covers:

- `database_analytics`
- `outlier_detection`
- `dbscan_clustering`
- `robot_collision_screening`

## Command 2: Same-Pod Deferred Exploration Batch

If Command 1 completes and the pod is still healthy, run this before shutdown:

```bash
cd /workspace/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal769_rtx_pod_one_shot.py \
  --branch codex/rtx-cloud-run-2026-04-22 \
  --optix-prefix /workspace/vendor/optix-dev-9.0.0 \
  --include-deferred \
  --only graph_analytics \
  --only service_coverage_gaps \
  --only event_hotspot_screening \
  --only road_hazard_screening \
  --only segment_polygon_hitcount \
  --only segment_polygon_anyhit_rows \
  --only hausdorff_distance \
  --only ann_candidate_search \
  --only facility_knn_assignment \
  --only barnes_hut_force_app \
  --only polygon_pair_overlap_area_rows \
  --only polygon_set_jaccard \
  --output-json docs/reports/goal769_rtx_pod_one_shot_summary_deferred_latest.json \
  --artifact-json docs/reports/goal762_rtx_cloud_artifact_report_deferred_latest.json \
  --artifact-md docs/reports/goal762_rtx_cloud_artifact_report_deferred_latest.md \
  --bundle-tgz docs/reports/goal769_rtx_pod_artifacts_deferred_latest.tgz
```

The deferred batch is allowed to fail. Preserve failures as artifacts and use
them for follow-up local work. Do not treat deferred success or failure as a
public speedup claim by itself.

## Copy Back

Copy these files back before stopping the pod:

- `docs/reports/goal769_rtx_pod_artifacts_latest.tgz`
- `docs/reports/goal769_rtx_pod_one_shot_summary_latest.json`
- `docs/reports/goal762_rtx_cloud_artifact_report_latest.json`
- `docs/reports/goal762_rtx_cloud_artifact_report_latest.md`
- `docs/reports/goal769_rtx_pod_artifacts_deferred_latest.tgz`
- `docs/reports/goal769_rtx_pod_one_shot_summary_deferred_latest.json`
- `docs/reports/goal762_rtx_cloud_artifact_report_deferred_latest.json`
- `docs/reports/goal762_rtx_cloud_artifact_report_deferred_latest.md`

## Shutdown Rule

After copying artifacts back, stop or terminate the pod. Do not keep cloud
running while local review, doc updates, or follow-up fixes happen.

## Claim Boundary

This packet authorizes starting a cloud evidence collection session. It does
not authorize public RTX speedup claims. Claims still require artifact review,
phase separation, correctness checks, hardware metadata, and baseline
comparison.

Short form: does not authorize public RTX speedup claims.
