# Handoff: Gemini Review for Goal2447/2449/2450 RT-DBSCAN Workspace Reuse

Please perform an independent read-only review of the current RTDL workspace.

## Context

Recent RT-DBSCAN work explored whether the chunked OptiX adjacency path can get
faster by reusing the `neighbor_indices` workspace:

- Goal2447: explicit single-workspace reuse option.
- Goal2449: bounded workspace pool option.
- Goal2450: pod smoke evidence showing those workspace variants are correct but
  not faster than default per-chunk allocation on the 32,768-point clustered
  row.

The engine must remain app-agnostic. These changes must be generic
fixed-radius graph/component runtime options, not DBSCAN-native ABI.

## Files to Inspect

- `src/rtdsl/partner_adapters.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `scripts/goal2403_rt_dbscan_repeat_probe.py`
- `tests/goal2447_rt_dbscan_neighbor_workspace_reuse_test.py`
- `tests/goal2449_rt_dbscan_neighbor_workspace_pool_test.py`
- `tests/goal2450_rt_dbscan_workspace_reuse_negative_evidence_test.py`
- `docs/reports/goal2447_rt_dbscan_neighbor_workspace_reuse_2026-05-19.md`
- `docs/reports/goal2449_rt_dbscan_neighbor_workspace_pool_2026-05-19.md`
- `docs/reports/goal2450_rt_dbscan_workspace_reuse_negative_evidence_2026-05-19.md`
- `docs/reports/goal2447_rt_dbscan_neighbor_workspace_reuse_pod_smoke/summary.json`
- `docs/reports/goal2449_rt_dbscan_neighbor_workspace_pool_pod_smoke/summary.json`
- `docs/research/future_version_to_do_list.md`

## Review Questions

1. Do the runtime/API changes preserve the generic fixed-radius graph/component
   contract and avoid DBSCAN-specific native logic?
2. Is the default still the fastest/safest path, with workspace reuse disabled
   unless explicitly requested?
3. Do the pod artifacts support the Goal2450 negative-performance conclusion?
4. Are claim boundaries accurate, especially no release, paper-reproduction,
   broad RT-core, or whole-app speedup claim?
5. Should the next direction be the larger generic grouped stream continuation
   rather than more neighbor-workspace tuning?

## Required Output

Write a review to:

`docs/reviews/goal2451_gemini_review_goal2447_2449_2450_workspace_reuse_2026-05-19.md`

Use one of the usual verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.
