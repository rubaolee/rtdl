# RTDL v1.5 Release Statement

Status: released. The `v1.5` annotated tag was published after explicit release
authorization.

The previous public release remains `v1.0`; it was not moved or retagged.

Release statement:

> RTDL v1.5 is the standalone Embree+OptiX language/runtime completion release
> for the supported v1.5 surface. It stabilizes the generic
> traversal-plus-reduction primitive layer for `ANY_HIT`, `COUNT_HITS`,
> `REDUCE_FLOAT(MIN|MAX|SUM)`, and `REDUCE_INT(COUNT|SUM)`, records 14 included
> app contracts with same-contract correctness and benchmark evidence, and
> explicitly excludes row-returning `COLLECT_K_BOUNDED` apps until v1.5.1. The
> stable primitive layer is app-name-free, but the native engine implementation
> is not yet app-agnostic internally.

## What This Release May Claim

- RTDL has a standalone Embree+OptiX language/runtime surface for the supported
  v1.5 contracts.
- The stable v1.5 primitive set is `ANY_HIT`, `COUNT_HITS`,
  `REDUCE_FLOAT(MIN|MAX|SUM)`, and `REDUCE_INT(COUNT|SUM)`.
- The v1.5 release includes 14 included app contracts and 4 excluded app rows.
- The included apps have same-contract correctness, benchmark evidence, and
  support-maturity gates recorded in the v1.5 reports.
- `COLLECT_K_BOUNDED` remains experimental in v1.5 and moves to the v1.5.1
  promotion track.
- Source-tree usage remains `PYTHONPATH=src:. python ...`.
- v1.6 through v2.0 are the staged partner-mechanism track.
- The app-agnostic engine target remains future work: v1.5.1 promotes
  `COLLECT_K_BOUNDED`, and v1.6-v2.0 move native execution toward primitive
  packets plus partner mechanisms.

## What This Release Must Not Claim

- a move or retag of `v1.0`;
- package-install support beyond source-tree execution;
- no whole-app speedup restriction;
- new broad public speedup wording for graph, DB, polygon, Jaccard, ANN,
  DBSCAN, robot, Barnes-Hut, or any other whole app;
- that every `--backend optix` run is a NVIDIA RT-core speedup;
- that `COLLECT_K_BOUNDED` is stable;
- that Vulkan, HIPRT, or Apple RT are active v1.5 backends.
- that the native engine is app-agnostic internally or has app-free internals.

## Evidence Pointers

- `/Users/rl2025/rtdl_python_only/docs/reports/goal1394_three_ai_v1_5_public_wording_consensus_2026-05-06.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal1397_three_ai_v1_5_standalone_partner_roadmap_consensus_2026-05-06.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal1400_v1_5_standalone_app_classification_2026-05-06.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal1402_v1_5_pending_app_correctness_closure_2026-05-06.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal1405_v1_5_support_maturity_matrix_2026-05-06.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal1406_v1_5_benchmark_evidence_matrix_2026-05-06.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal1410_v1_5_vs_v1_0_rtx_pod_perf_results_2026-05-06.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal1411_v1_5_boundary_backend_consensus_status_2026-05-06.md`
