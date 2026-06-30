# RTDL v1.5 Release Package

Status: released. The `v1.5` annotated tag was published after explicit release
authorization.

The previous public release remains `v1.0`; it was not moved or retagged.

RTDL v1.5 is the standalone Embree+OptiX language/runtime completion release
for the supported v1.5 surface. It packages the stable generic
traversal-plus-reduction primitive layer, classifies the public app set, and
records same-contract correctness, benchmark evidence, and support maturity for
the included apps.

v1.5 is not yet app-agnostic inside the native engine implementation. The
stable primitive layer is app-name-free, but some native Embree/OptiX entry
points remain workload-shaped compatibility/proof surfaces. Removing or
formalizing that remaining app knowledge starts with `COLLECT_K_BOUNDED` in
v1.5.1 and continues through the v1.6-v2.0 partner mechanism track.

## Scope

This package records the v1.5 boundary:

- standalone Embree+OptiX language/runtime support for the included v1.5
  surface;
- stable primitive names: `ANY_HIT`, `COUNT_HITS`,
  `REDUCE_FLOAT(MIN|MAX|SUM)`, and `REDUCE_INT(COUNT|SUM)`;
- 14 included public app contracts with same-contract correctness and benchmark
  evidence;
- 4 excluded public app rows: `apple_rt_demo`, `hiprt_ray_triangle_hitcount`,
  `polygon_set_jaccard`, and `segment_polygon_anyhit_rows`;
- `COLLECT_K_BOUNDED` remains experimental in v1.5;
- row-returning `COLLECT_K_BOUNDED` apps are deferred to v1.5.1;
- source-tree usage remains `PYTHONPATH=src:. python ...`;
- Vulkan, HIPRT, and Apple RT are preserved proof surfaces, but they are not
  active v1.5 implementation targets;
- the native engine is not yet app-agnostic internally.

## Allowed Conclusion

RTDL v1.5 is the standalone Embree+OptiX language/runtime completion release
for the supported v1.5 surface: generic traversal-plus-reduction primitives, 14
included app contracts, explicit exclusion of row-returning `COLLECT_K_BOUNDED`
apps, no new whole-app speedup claim, and no claim that the native engine has
app-free internals.

## Disallowed Conclusions

- that the v1.5 release moves or retags `v1.0`;
- that `v1.0` has been moved or retagged;
- package-install support beyond source-tree execution;
- no whole-app speedup boundary being removed;
- broad NVIDIA RTX, GPU, graph, DB, polygon, ANN, DBSCAN, robot, or Barnes-Hut
  speedup claims;
- promotion of `COLLECT_K_BOUNDED` to stable status;
- treating Vulkan, HIPRT, or Apple RT as active v1.5 backends.
- claiming the native engine is app-agnostic internally.

## Start Here

- [Release Statement](release_statement.md)
- [Support Matrix](support_matrix.md)
- [Audit Report](audit_report.md)
- [Tag Preparation](tag_preparation.md)
- [v1.5 Benchmark Evidence Report](../../reports/goal1406_v1_5_benchmark_evidence_matrix_2026-05-06.md)
- [v1.5 Support/Maturity Report](../../reports/goal1405_v1_5_support_maturity_matrix_2026-05-06.md)
- [v1.5 Correctness Closure](../../reports/goal1402_v1_5_pending_app_correctness_closure_2026-05-06.md)
- [v1.5 App Classification](../../reports/goal1400_v1_5_standalone_app_classification_2026-05-06.md)
- [v1.5 Public Wording 3-AI Consensus](../../reports/goal1394_three_ai_v1_5_public_wording_consensus_2026-05-06.md)
- [v1.5 Boundary/Backend 3-AI Consensus](../../reports/goal1411_v1_5_boundary_backend_consensus_status_2026-05-06.md)
- [RTX Pod v1.5 vs v1.0 Performance Results](../../reports/goal1410_v1_5_vs_v1_0_rtx_pod_perf_results_2026-05-06.md)
- [App-Independent Engine Roadmap](../../reports/goal1413_app_independent_engine_roadmap_2026-05-06.md)

## Release Gate State

All implementation-facing standalone gates are complete: classification,
`COLLECT_K_BOUNDED` exclusion, same-contract correctness, benchmark evidence,
support maturity, release-docs/public-wording, boundary/backend consensus, and
the app-independent engine roadmap. The `v1.5` tag has been published; no
package-install, whole-app speedup, or zero-app-knowledge native-engine claim is
added by this release.
