# Goal907: Graph Matrix Source Sync After Goal906

Date: 2026-04-24

## Purpose

Goal906 updated the public graph RT documentation after Goals 903-905, but a follow-up scan found stale graph-readiness language in the source app-support matrix used by generated release-gate artifacts.

This Goal907 change synchronizes the source matrix with the current graph state:

- `visibility_edges` remains a bounded graph-to-RT any-hit path.
- Embree BFS and triangle-count now use ray traversal over graph-edge primitives for candidate generation.
- OptiX BFS and triangle-count now expose explicit native graph-ray mode behind `--optix-graph-mode native` / `RTDL_OPTIX_GRAPH_MODE=native`.
- The combined Goal889/905 cloud gate must pass on real RTX hardware before any NVIDIA graph RT-core claim.
- CPU-side BFS frontier bookkeeping and triangle neighbor-set intersection remain outside the RT-core claim.
- There is still no claim for shortest-path, graph database, distributed graph analytics, or whole-app graph-system acceleration.

## Files Changed

- `src/rtdsl/app_support_matrix.py`: replaced stale visibility-only Goal889 wording with combined Goal889/905 wording.
- `docs/reports/goal848_v1_0_rt_core_goal_series_2026-04-23.json`: regenerated from the source matrix.
- `docs/reports/goal901_pre_cloud_app_closure_gate_2026-04-24.json`: regenerated closure metadata after the matrix change.
- `docs/reports/goal824_pre_cloud_rtx_readiness_gate_2026-04-23.json`: regenerated readiness metadata after the matrix change.

`docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json` was also regenerated and already matched the current Goal889/905 graph-gate language, so it produced no content diff.

## Verification

Command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal848_v1_rt_core_goal_series_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal901_pre_cloud_app_closure_gate_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test \
  tests.goal814_graph_optix_rt_core_honesty_gate_test \
  tests.goal821_public_docs_require_rt_core_test \
  tests.goal868_graph_redesign_decision_packet_test \
  tests.goal889_graph_visibility_optix_gate_test -v
```

Result: `Ran 41 tests in 2.878s - OK`.

Additional checks:

```bash
PYTHONPATH=src:. python3 -m py_compile \
  src/rtdsl/app_support_matrix.py \
  scripts/goal848_v1_rt_core_goal_series.py \
  scripts/goal759_rtx_cloud_benchmark_manifest.py \
  scripts/goal889_graph_visibility_optix_gate.py

git diff --check
```

Result: both checks passed.

## Boundary

Goal907 is documentation/artifact synchronization only. It does not add new graph execution behavior and does not authorize NVIDIA RT-core performance claims. Graph claims still require a passing real RTX artifact from the combined Goal889/905 cloud gate and independent review.
