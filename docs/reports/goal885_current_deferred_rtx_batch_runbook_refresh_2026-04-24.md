# Goal885 Current Deferred RTX Batch Runbook Refresh

Date: 2026-04-24

## Result

Goal885 refreshes the single-session RTX cloud runbook so it matches the
current v0.9.8 app state after Goals879-884.

The runbook still requires the active evidence batch first. It now also records
a same-pod deferred exploration batch covering all current deferred targets:

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

## Boundary

The deferred batch is explicitly exploratory. It may expose failures, and those
failures must be preserved as artifacts and treated as follow-up work. It does
not authorize public RTX speedup claims.

The active batch remains the first command because it is the cleaner
release-grade evidence path. Deferred gates run second only if the pod is still
healthy, so one pod session can collect more information without mixing active
evidence with exploratory promotion work.

## Dry-Run Verification

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal769_rtx_pod_one_shot_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test
```

Result: `10 tests OK`.

Deferred one-shot dry-run:

```bash
PYTHONPATH=src:. python3 scripts/goal769_rtx_pod_one_shot.py \
  --dry-run \
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
  --output-json build/goal885_deferred_one_shot_dry_run.json \
  --artifact-json build/goal885_deferred_artifact.json \
  --artifact-md build/goal885_deferred_artifact.md \
  --bundle-tgz build/goal885_deferred_bundle.tgz
```

Result: `status: ok`, `include_deferred: true`, `only_count: 10`.

## Current Pod Estimate

If no new local code changes are added before cloud, the pod can be started
after Goal885 is reviewed, committed, and pushed. The intended pod session is:

1. Active one-shot batch.
2. Same-pod deferred exploration batch.
3. Copy artifacts back.
4. Stop or terminate the pod.

