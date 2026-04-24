# RTX Cloud Single-Session Runbook

This runbook is for paid NVIDIA RTX pod time. It exists to avoid repeated
restart/stop cycles while RTDL is validating NVIDIA RT-core app evidence.

## Before Starting A Pod

Run this locally first:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal824_pre_cloud_rtx_readiness_gate.py \
  --output-json docs/reports/goal824_pre_cloud_rtx_readiness_gate_2026-04-23.json
```

Start a pod only if the result is:

```text
"valid": true
```

Do not start a pod for one app at a time.

## Recommended Pod Shape

Use an RTX-class NVIDIA GPU with real RT cores. Acceptable examples:

- RTX 4090
- RTX A5000/A6000
- L4
- A10/A10G

Avoid GTX 1070-class GPUs for RT-core claims. They can test CUDA/OptiX behavior
but not NVIDIA RT-core acceleration.

## One Command On The Pod

After SSH into the pod and checking out the repo, run one batched command:

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

## Same-Pod Deferred Exploration Batch

Run the active one-shot command first. If it succeeds and the pod is still
healthy, use the same pod for deferred evidence before shutdown. This keeps
cloud cost under control while preserving the difference between release-grade
active evidence and exploratory/deferred gates.

Short form: release-grade active evidence first; exploratory/deferred gates
second.

Current deferred targets:

- `service_coverage_gaps`
- `event_hotspot_screening`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `hausdorff_distance`
- `ann_candidate_search`
- `facility_knn_assignment`
- `barnes_hut_force_app`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

Use this deferred batch command:

```bash
cd /workspace/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal769_rtx_pod_one_shot.py \
  --branch codex/rtx-cloud-run-2026-04-22 \
  --optix-prefix /workspace/vendor/optix-dev-9.0.0 \
  --include-deferred \
  --only service_coverage_gaps \
  --only event_hotspot_screening \
  --only segment_polygon_hitcount \
  --only segment_polygon_anyhit_rows \
  --only hausdorff_distance \
  --only ann_candidate_search \
  --only facility_knn_assignment \
  --only barnes_hut_force_app \
  --only polygon_pair_overlap_area_rows \
  --only polygon_set_jaccard \
  --output-json docs/reports/goal769_rtx_pod_one_shot_summary_latest.json \
  --artifact-json docs/reports/goal762_rtx_cloud_artifact_report_latest.json \
  --artifact-md docs/reports/goal762_rtx_cloud_artifact_report_latest.md \
  --bundle-tgz docs/reports/goal769_rtx_pod_artifacts_latest.tgz
```

The deferred batch is allowed to expose failures. Preserve all artifacts and
treat failures as local follow-up work, not as public RTX claim evidence.

## Required Success Conditions

The one-shot summary must report:

```text
"status": "ok"
```

The artifact report must report:

```text
"status": "ok"
```

Every non-dry-run artifact must include:

- `cloud_claim_contract`
- `required_phase_groups`
- all required phase keys for that app

If any result is `failed` or `needs_attention`, preserve the generated reports
and stop interpreting performance numbers as claim evidence.

## Files To Copy Back

Copy the bundle first:

```text
docs/reports/goal769_rtx_pod_artifacts_latest.tgz
```

Also copy these individual files if available:

- `docs/reports/goal769_rtx_pod_one_shot_summary_latest.json`
- `docs/reports/goal762_rtx_cloud_artifact_report_latest.json`
- `docs/reports/goal762_rtx_cloud_artifact_report_latest.md`
- `docs/reports/goal761_rtx_cloud_run_all_summary.json`
- `docs/reports/goal763_rtx_cloud_bootstrap_check.json`
- `docs/reports/goal759_*_rtx.json`

## Shutdown Rule

After copying artifacts back, stop or terminate the pod. Do not keep it running
while local code/doc review happens.

If the run fails because of a missing dependency or environment problem, fix as
much as possible locally before starting another pod.

## Claim Boundary

This runbook collects evidence. It does not authorize public RTX speedup claims.
Claims still require review of hardware metadata, correctness, phase separation,
artifact contracts, and comparison baselines.
