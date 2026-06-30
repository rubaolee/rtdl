# Handoff: Gemini Review For Goal2441/2442 Adaptive Chunk Budget

Please perform an independent read-only review and write the result to:

`docs/reviews/goal2443_gemini_review_goal2441_2442_adaptive_chunk_budget_2026-05-19.md`

## Context

Goal2441 changes the RT-DBSCAN chunked OptiX adjacency continuation so
`max_directed_edges_per_chunk` becomes an adaptive degree-budget chunk planner
instead of a late failure check over fixed 4096-point chunks.

Goal2442 pod-smokes that behavior on `clustered3d` with 32,768 points and
`--chunk-adjacency-edge-budget 8000000`.

Files to inspect:

- `src/rtdsl/partner_adapters.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/README.md`
- `tests/goal2441_rt_dbscan_adaptive_chunk_budget_test.py`
- `tests/goal2442_rt_dbscan_adaptive_chunk_budget_pod_smoke_test.py`
- `docs/reports/goal2441_rt_dbscan_adaptive_chunk_budget_2026-05-19.md`
- `docs/reports/goal2442_rt_dbscan_adaptive_chunk_budget_pod_smoke_2026-05-19.md`
- `docs/reports/goal2442_rt_dbscan_adaptive_chunk_budget_pod_smoke/summary.json`
- `docs/reports/goal2442_rt_dbscan_adaptive_chunk_budget_pod_smoke/clustered32768_chunk_budget_8000000.json`

## Review Questions

1. Does the implementation preserve the app-agnostic native-engine boundary?
2. Does the helper split chunks by both point count and directed-edge budget?
3. Does the pod artifact prove the requested 8M directed-edge cap was enforced
   (`max_chunk_directed_edge_count <= 8000000`)?
4. Does the report correctly frame this as memory control rather than speedup?
5. Are the local tests sufficient for the pure helper and metadata, with the pod
   smoke sufficient for runtime evidence?

Use one verdict only:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`
