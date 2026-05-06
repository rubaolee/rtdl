# RTDL v1.5 Release-Candidate Package

Status: release candidate ready; not tagged until an explicit release/tag action.

The current released version remains `v1.0` until that explicit release action
is performed.

RTDL v1.5 is the standalone Embree+OptiX language/runtime completion candidate
for the supported v1.5 surface. It packages the stable generic
traversal-plus-reduction primitive layer, classifies the public app set, and
records same-contract correctness, benchmark evidence, and support maturity for
the included apps.

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
  active v1.5 implementation targets.

## Allowed Conclusion

RTDL v1.5 is the standalone Embree+OptiX language/runtime completion candidate
for the supported v1.5 surface: generic traversal-plus-reduction primitives, 14
included app contracts, explicit exclusion of row-returning `COLLECT_K_BOUNDED`
apps, and no new whole-app speedup claim.

## Disallowed Conclusions

- that a v1.5 tag exists before an explicit release/tag action;
- that `v1.0` has been moved or retagged;
- package-install support beyond source-tree execution;
- no whole-app speedup boundary being removed;
- broad NVIDIA RTX, GPU, graph, DB, polygon, ANN, DBSCAN, robot, or Barnes-Hut
  speedup claims;
- promotion of `COLLECT_K_BOUNDED` to stable status;
- treating Vulkan, HIPRT, or Apple RT as active v1.5 backends.

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

## Release Gate State

All implementation-facing standalone gates are complete: classification,
`COLLECT_K_BOUNDED` exclusion, same-contract correctness, benchmark evidence,
and support maturity. This package closes the release-docs/public-wording gate
as a release candidate, but tag creation still requires an explicit release/tag
action.
