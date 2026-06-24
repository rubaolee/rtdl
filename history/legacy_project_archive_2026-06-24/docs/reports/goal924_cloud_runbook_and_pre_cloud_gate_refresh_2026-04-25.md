# Goal 924: Cloud Runbook and Pre-Cloud Gate Refresh

Date: 2026-04-25

## Scope

Refresh the paid RTX cloud execution guidance after Goals 918-923 changed the
v1.0 NVIDIA RT-core app board.

This goal is documentation and gate synchronization only. It does not add RTX
performance evidence, does not start a cloud pod, and does not authorize any
public speedup claim.

## Changes

- Updated `docs/rtx_cloud_single_session_runbook.md` so the old Goal913
  graph/Jaccard-only retry path is explicitly historical, while the current
  post-Goal923 policy is to use the OOM-safe groups for the consolidated v1.0
  batch.
- Added driver/header guidance for both observed RTX pod environments:
  driver `550.127.05` with OptiX SDK headers `v8.0.0`, and driver
  `580.126.09` or newer with OptiX SDK headers `v9.0.0`.
- Refreshed the deferred-target list to the current nine remaining deferred
  NVIDIA-target apps:
  `graph_analytics`, `road_hazard_screening`, `segment_polygon_hitcount`,
  `segment_polygon_anyhit_rows`, `hausdorff_distance`, `ann_candidate_search`,
  `barnes_hut_force_app`, `polygon_pair_overlap_area_rows`, and
  `polygon_set_jaccard`.
- Fixed the targeted graph retry example to use the manifest path
  `graph_visibility_edges_gate` rather than the public app name
  `graph_analytics`.
- Updated Goal824 pre-cloud readiness gate policy to match the OOM-safe
  runbook flow instead of stale full-batch `Goal769` wording.
- Updated tests for the current 8 active entries, 9 deferred entries, 17 total
  cloud entries, and 16 unique commands.

## Local Gate Result

`scripts/goal824_pre_cloud_rtx_readiness_gate.py` now reports:

- `valid: true`
- `active_count: 8`
- `deferred_count: 9`
- `baseline_contract_count: 17`
- `missing_deferred: []`
- `missing_excluded: []`

The gate remains local-only and still says it does not start cloud or authorize
speedup claims.

## Verification

Focused verification:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal901_pre_cloud_app_closure_gate_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test
```

Result: 25 tests OK.

## Boundary

This closes a pre-cloud process/documentation mismatch. The remaining app
readiness claims still require real RTX artifacts, copied-back group summaries,
Goal762 artifact analysis, and independent review.
