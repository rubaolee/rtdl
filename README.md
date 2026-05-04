# RTDL

RTDL is a Python-hosted DSL/runtime for non-graphical workloads that can be
expressed as ray-tracing-style search: build an acceleration structure, traverse
it, refine candidate hits, and emit stable rows for an application.

The project goal is practical: let Python users write application-shaped
spatial, graph-adjacent, nearest-neighbor, simulation-screening, and
database-style kernels without hand-building every backend path. RTDL owns the
traversal/refinement machinery; Python owns the app logic unless a documented
native continuation exists for the current v1.0 proof.

The current released version is `v0.9.8`.
- current released version: `v0.9.8`

## Start Fast

```bash
python3 -m pip install -e .
PYTHONPATH=src:. python examples/rtdl_hello_world.py
PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend embree
```

Useful first reads:

- [Public Documentation Map](docs/public_documentation_map.md)
- [Quick Tutorial](docs/quick_tutorial.md)
- [App And Example Quickstart](docs/app_example_quickstart.md)
- [Release-Facing Examples](docs/release_facing_examples.md)
- [Application Catalog](docs/application_catalog.md)
- [v1.0 App Acceleration Inventory](docs/v1_0_app_acceleration_inventory.md)
- [RTDL Current Main Support Matrix](docs/current_main_support_matrix.md)
- [Engine Feature Support Contract](docs/features/engine_support_matrix.md)
- [Performance Model](docs/performance_model.md)
- [v1.0 RTX App Status](docs/v1_0_rtx_app_status.md)
- [Docs Index](docs/README.md)

## Current Status

| Area | State |
| --- | --- |
| Release | current released version: `v0.9.8` |
| v1.0 mainline | foundation work for app-shaped RTDL proof, documentation, and bounded app evidence |
| Public RTX wording | `12 reviewed` bounded RTX sub-path rows after Goal1224 |
| Still blocked | `graph_analytics`, `polygon_pair_overlap_area_rows` public speedup wording |
| Not yet public-reviewed | `database_analytics`, `polygon_set_jaccard` public speedup wording |
| Non-NVIDIA proof lines | HIPRT, Vulkan, and Apple RT prove selected backend surfaces, but are not the v1.0 NVIDIA RTX evidence path |

RTDL is not a general-purpose renderer or graphics engine. The demo assets show
that the same compute core can drive bounded Python applications; they are not a
graphics-product claim.

## v1.0 Direction

v1.0 is for proving that a Python-hosted RT DSL works on real
application-shaped workloads. It is allowed to use app-specific engine
customization where needed to make supported apps measurable and useful. That is
v1.0 proof machinery, not the final architecture.

v1.5 is planned to replace app-specific engine customization with reviewed
generic traversal-plus-reduction primitives. v2.0 targets broader end-to-end performance through explicit zero-copy partnership with GPU compute tools for
the non-RT phases.

The released `v0.8.0` app-building examples remain the simplest way to see this
pattern in Python:

- `examples/rtdl_hausdorff_distance_app.py`
- `examples/rtdl_ann_candidate_app.py`
- `examples/rtdl_outlier_detection_app.py`
- `examples/rtdl_dbscan_clustering_app.py`
- `examples/rtdl_robot_collision_screening_app.py`
- `examples/rtdl_barnes_hut_force_app.py`
- `examples/rtdl_database_analytics_app.py`
- `examples/rtdl_apple_rt_demo_app.py`
- tutorial: `docs/tutorials/v0_8_app_building.md`

These apps use existing RTDL features and Python-owned application logic; they
are not a new released backend/language surface.

## NVIDIA RT-Core Claim Boundary

`--backend optix` means an app selected an OptiX-capable execution path. It is
not, by itself, a public claim that NVIDIA RT cores accelerated the app. Public
RTX wording requires `--require-rt-core`, valid same-contract evidence, and a
saved review trail.

The front-page rule is simple:

- Claim the exact reviewed prepared/native sub-path, not the whole app.
- Do not generalize from one OptiX mode to all OptiX modes.
- Do not count Python post-processing, exact polygon refinement, SQL/DBMS
  behavior, ANN ranking, DBSCAN expansion, graph-system analytics, or
  Barnes-Hut force reduction unless a later review explicitly authorizes it.
- Treat the support matrix and v1.0 inventory as the authority for current
  wording.

Reviewed examples include bounded public sub-path wording for
`service_coverage_gaps / prepared_gap_summary`,
`event_hotspot_screening / prepared_count_summary`,
`outlier_detection / prepared_fixed_radius_density_summary`,
`dbscan_clustering / prepared_fixed_radius_core_flags`,
`segment_polygon_hitcount / segment_polygon_hitcount_native_experimental`,
`segment_polygon_anyhit_rows / segment_polygon_anyhit_rows_prepared_bounded_gate`,
`ann_candidate_search / candidate_threshold_prepared`,
`facility_knn_assignment / coverage_threshold_prepared_recentered`,
`road_hazard_screening / prepared_native_compact_summary_40k`,
`barnes_hut_force_app / node_coverage_prepared_rich`,
`robot_collision_screening / prepared_pose_flags`, and
`hausdorff_distance / directed_threshold_prepared`.

These are not automatic public speedup claims. Each line is not a whole-app, default-mode, Python-postprocess, or broad RT-core acceleration claim.

Examples of reviewed wording boundaries:

- Facility KNN: `0.111619` s, `80.60x` for the prepared facility
  coverage-threshold query sub-path only.
- Road hazard: `0.230652` s, `3.53x` for the prepared native compact-summary
  traversal/count sub-path at 40k copies only.
- Barnes-Hut: `0.222256` s, `240.56x` for the prepared node-coverage query
  only, not force reduction.
- Robot collision: `918.91x normalized per-pose` for `prepared_pose_flags`
  only; this is not a same-total-work wall-time claim, not a whole-app robot-planning claim, and witness-row output remains outside the wording.

Still outside public RTX claim review today: SQL/DBMS behavior, default
row-materializing DB output, full road-hazard/GIS routing, prepared road hazard
row output, unbounded segment/polygon pair-row volume, Hausdorff exact distance,
ANN ranking, DBSCAN cluster expansion, graph-system claims, and Barnes-Hut force
reduction/opening-rule acceleration.

Claim-sensitive command shapes are documented in the app docs and support
matrix. Representative examples include:

```bash
--backend optix --output-mode compact_summary --require-rt-core
--backend optix --scenario visibility_edges --require-rt-core
--backend optix --optix-summary-mode gap_summary_prepared --require-rt-core
--backend optix --optix-summary-mode count_summary_prepared --require-rt-core
--backend optix --optix-summary-mode coverage_threshold_prepared --require-rt-core
--backend optix --output-mode summary --optix-mode native --require-rt-core
--backend optix --optix-summary-mode directed_threshold_prepared --require-rt-core
--backend optix --optix-summary-mode candidate_threshold_prepared --require-rt-core
--backend optix --optix-summary-mode rt_count_threshold_prepared --output-mode density_count
--backend optix --optix-summary-mode rt_core_flags_prepared --output-mode core_count
--backend optix --optix-summary-mode prepared_count
--backend optix --optix-summary-mode node_coverage_prepared --require-rt-core
```

Also see the prepared native hit-count traversal, prepared bounded native pair-row traversal, polygon pair overlap, polygon set Jaccard, and
`prepared_pose_flags` entries in the linked status pages.

Detailed evidence and review trail:

- [v1.0 RTX App Status](docs/v1_0_rtx_app_status.md)
- [v1.0 App Acceleration Inventory](docs/v1_0_app_acceleration_inventory.md)
- [App Engine Support Matrix](docs/app_engine_support_matrix.md)
- [Performance Model](docs/performance_model.md)
- [Large Repeat Artifact Intake](docs/reports/goal1008_large_repeat_artifact_intake_2026-04-26.md)
- [Public RTX Wording Review Packet](docs/reports/goal1009_public_rtx_wording_review_packet_2026-04-26.md)
- [Three-AI Same-Semantics Consensus](docs/reports/goal1058_three_ai_same_semantics_consensus_2026-04-28.md)
- [Current-Source RTX Pod Run](docs/reports/goal1121_rtx_pod_current_source_run_report_2026-04-29.md)
- [Goal1123 Two-AI Consensus](docs/reports/goal1123_two_ai_consensus_2026-04-29.md)
- [Goal1126 Three-AI Consensus](docs/reports/goal1126_three_ai_consensus_2026-04-29.md)
- [Goal1142 Current-Source Replacement Evidence](docs/reports/goal1142_current_source_robot_64m_replacement_report_2026-04-29.md)
- [Goal1146 Public Wording Promotion Consensus](docs/reports/goal1146_two_ai_public_wording_promotion_consensus_2026-04-29.md)
- [Goal1208 Public Wording Consensus](docs/reports/goal1208_two_ai_consensus_2026-05-01.md)
- [RTX Wording Resolution Consensus](docs/reports/goal1224_two_ai_consensus_2026-05-01.md)
- [Goal1224 RTX Wording Resolution Consensus Alias](docs/reports/goal1224_two_ai_rtx_wording_resolution_consensus_2026-05-01.md)

Goal1177 is recovered clean-source RTX A5000 evidence for external-review input only.
Goal1184 records Goal1182 RTX A4500 batch evidence as external-review input only.
Neither goal adds a new reviewed public wording row or authorizes public speedup wording.
They do not authorize public speedup wording.
Goal1177 does not authorize public speedup wording.

Goal748 is the robot OptiX erratum boundary: pre-Goal748 robot OptiX evidence
used a short-ray `optixReportIntersection` path later fixed by Goal748. Use the
post-fix Goal748 parity/performance report or later robot OptiX evidence for
current claims.

## What RTDL Contains

| Capability | Public shape |
| --- | --- |
| Geometry rows | `knn_rows`, `bounded_knn_rows`, `fixed_radius_neighbors`, exact closest-hit paths |
| Any-hit traversal | `ray_triangle_any_hit`, visibility rows, prepared repeated-query visibility/count helpers |
| Reductions | `reduce_rows` in Python; native reductions are a v1.5 design target |
| IR and lowering | `CompiledKernel` lowers to `RTExecutionPlan`; see [IR And Lowering](docs/rtdl/ir_and_lowering.md) |
| Backends | CPU reference, Embree, OptiX, HIPRT, Vulkan, Apple RT/MPS RT where documented |
| Apps | Hausdorff, ANN candidate search, outlier detection, DBSCAN core flags, robot collision screening, Barnes-Hut node coverage, graph visibility, database-style summaries, road hazard, segment/polygon summaries |

`ray_triangle_any_hit`, `visibility_rows`, and `reduce_rows` are public RTDL
surfaces. OptiX, Embree, and HIPRT have native early-exit any-hit support in the
released line. Vulkan and Apple RT support selected any-hit/visibility
contracts, but some paths are not a native reduction or public speedup claim.

## Evidence And Releases

- [RTDL v0.9.8 Release Package](docs/release_reports/v0_9_8/README.md)
- [RTDL v0.9.8 Support Matrix](docs/release_reports/v0_9_8/support_matrix.md)
- [RTDL v0.9.6 Release Package](docs/release_reports/v0_9_6/README.md)
- [RTDL v0.9.5 Release Package](docs/release_reports/v0_9_5/README.md)
- [RTDL v0.9.5 Support Matrix](docs/release_reports/v0_9_5/support_matrix.md)
- [RTDL v0.9 Release Package](docs/release_reports/v0_9/README.md)
- [RTDL v0.8 Release Package](docs/release_reports/v0_8/README.md)
- [RTDL v0.8 Release Statement](docs/release_reports/v0_8/release_statement.md)
- [RTDL v0.8 Support Matrix](docs/release_reports/v0_8/support_matrix.md)
- [Hausdorff Linux Performance Evidence](docs/reports/goal507_hausdorff_linux_perf_report_2026-04-17.md)
- [Robot/Barnes-Hut Linux Performance Evidence](docs/reports/goal509_robot_barnes_linux_perf_report_2026-04-17.md)
- [Goal524 v0.8 Stage-1 Proximity Linux Performance](docs/reports/goal524_v0_8_stage1_proximity_linux_perf_2026-04-17.md)

RTX-class
      performance validation remains bounded to the reviewed prepared/native
      sub-paths named above.

`v0.9.5`: earlier public release for bounded any-hit, visibility rows, and
Python-side emitted-row reductions. For audit continuity: earlier Linux Goal509 evidence covered the hit-count formulation, Embree, and pre-fix OptiX; new backend speedup claims need fresh gates and should use the post-fix Goal748 short-ray parity/performance report
instead of the old robot OptiX result. Barnes-Hut now has bounded Linux CPU/Embree/OptiX/Vulkan evidence that separates candidate-generation timing
from Python opening-rule and force-reduction timing.

The Hausdorff Linux Performance Evidence covers Embree, OptiX, Vulkan, SciPy,
and FAISS baselines. It supports bounded backend evidence but does not show RTDL
beating the strongest mature exact nearest-neighbor library baselines.

Goal524 characterizes ANN candidate, outlier, and DBSCAN proximity apps. SciPy
was not installed in that gate, so the result is not an external-baseline
speedup claim.

## Demo

- [Watch the public 4K demo video](https://www.youtube.com/watch?v=d3yJB7AmCLM)
- [Short 4K demo URL](https://youtu.be/d3yJB7AmCLM)
- Primary visual demo: `examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py`

## Repository Layout

| Path | Purpose |
| --- | --- |
| `src/rtdsl/` | Python DSL/runtime and backend adapters |
| `examples/` | Public example apps and demos |
| `docs/` | User docs, architecture docs, tutorials, release packages |
| `docs/reports/` | Goal reports, reviews, consensus records, benchmark evidence |
| `tests/` | Regression tests for API, docs, release gates, and claim boundaries |
| `scripts/` | Audits, report generators, and benchmark/intake helpers |

For full navigation, start with [docs/README.md](docs/README.md).
