# Goal905: Graph Native OptiX Cloud Gate Packaging

Date: 2026-04-24

## Verdict

Packaged the new Goal904 native OptiX graph-ray BFS and triangle-count paths into
the existing deferred graph RTX gate. The next paid cloud batch will no longer
validate only `visibility_edges`; it will validate three bounded graph RT
sub-paths in one artifact:

- `visibility_edges`: OptiX ray/triangle any-hit over blocker geometry
- `bfs`: explicit native OptiX graph-ray candidate generation
- `triangle_count`: explicit native OptiX graph-ray candidate generation

## What Changed

`scripts/goal889_graph_visibility_optix_gate.py` now runs CPU references for all
three graph scenarios and then attempts matching OptiX paths:

- `optix_visibility_anyhit`
- `optix_native_graph_ray_bfs`
- `optix_native_graph_ray_triangle_count`

The gate computes row digests from row-mode execution for correctness parity, but
can emit compact summary artifacts without storing all rows. This keeps the cloud
artifact useful for correctness review without forcing huge JSON payloads.

The Goal759 manifest and generated JSON now describe the graph gate as a combined
Goal889/905 gate rather than a visibility-only gate.

## Claim Boundary

This goal does not authorize a graph RTX speedup claim. The allowed future claim
scope is bounded to:

- visibility any-hit filtering
- BFS candidate generation by graph-edge ray traversal
- triangle-count candidate generation by graph-edge ray traversal

It explicitly excludes shortest path, graph databases, distributed graph
analytics, and whole-app graph-system acceleration. BFS visited/frontier state
management and triangle neighbor-set intersection remain outside the RT traversal.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest tests.goal759_rtx_cloud_benchmark_manifest_test tests.goal889_graph_visibility_optix_gate_test tests.goal901_pre_cloud_app_closure_gate_test tests.goal824_pre_cloud_rtx_readiness_gate_test -v
```

Result: `25` tests, `OK`.

```text
PYTHONPATH=src:. python3 -m py_compile scripts/goal889_graph_visibility_optix_gate.py scripts/goal759_rtx_cloud_benchmark_manifest.py tests/goal889_graph_visibility_optix_gate_test.py tests/goal759_rtx_cloud_benchmark_manifest_test.py
git diff --check
```

Result: both passed.

Regenerated artifacts:

- `docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json`
- `docs/reports/goal901_pre_cloud_app_closure_gate_2026-04-24.json`
- `docs/reports/goal824_pre_cloud_rtx_readiness_gate_2026-04-23.json`

## Next Gate

Run this only inside the single paid RTX full batch, not as a standalone pod
cycle:

```text
python3 scripts/goal769_rtx_pod_one_shot.py --include-deferred
```

The graph artifact still requires post-cloud independent review before any graph
RT-core claim can be promoted.
