# Handoff: Gemini Review For Goal2397/Goal2398 RT-DBSCAN Repair And Pod Evidence

Please perform a read-only independent review of the RT-DBSCAN benchmark campaign updates after Goal2394.

## Review Scope

Inspect:

- `src/rtdsl/partner_adapters.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `scripts/goal2392_rt_dbscan_pod_runner.sh`
- `docs/reports/goal2397_rt_dbscan_cupy_grid_union_repair_2026-05-19.md`
- `docs/reports/goal2398_rt_dbscan_clean_pod_evidence_2026-05-19.md`
- `docs/reports/goal2398_rt_dbscan_clean_pod_evidence/`
- `tests/goal2397_rt_dbscan_cupy_grid_union_repair_test.py`
- `tests/goal2398_rt_dbscan_clean_pod_evidence_test.py`

## Context

Goal2397 repaired the generic CuPy 3-D radius-graph component primitive. The old
CuPy raw-kernel union path used concurrent path-compression writes and timed out
on an RTX A5000 pod for the clustered 4096-point row. The repair uses a
monotonic `atomicMin` root-linking policy and skips duplicate undirected
core-edge unions. This must remain app-agnostic and must not introduce a native
DBSCAN ABI.

Goal2398 reran the pod evidence from a clean pushed commit:

```text
e5e6d4ca / environment artifact source commit 7b9cd29afd02c9790b8982b9d99423b34661d278
```

The pod artifacts record RTX A5000 driver 570.211.01, Python 3.12.3, CuPy
14.0.1. The clean evidence rows show:

- `clustered3d` 4096 host-bucket continuation: 1.983031 s
- `clustered3d` 4096 repaired CuPy device-grid continuation: 0.500779 s
- `road3d` 4096 host-bucket continuation: 0.949524 s
- `road3d` 4096 repaired CuPy device-grid continuation: 0.490753 s
- OptiX prepared-row rows completed at 1024 points but still materialize
  neighbor rows on the host.

## Questions To Answer

1. Does the Goal2397 repair correctly address the pathological CuPy component
   continuation without adding DBSCAN-specific native engine logic?
2. Are the Goal2398 pod artifacts internally consistent with the report and
   tests?
3. Are the claim boundaries correct: accept the CuPy device-grid repair as a
   stronger CUDA-core partner baseline, but do not claim RT-core/paper speedup
   or release readiness from this evidence alone?
4. Is the remaining architectural gap correctly stated as:
   `OptiX fixed-radius device output -> device-resident grouped/component continuation`?

## Required Output

Write the review to:

```text
docs/reviews/goal2399_gemini_review_goal2397_2398_rt_dbscan_repair_pod_evidence_2026-05-19.md
```

Use one of the project verdict words: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.
