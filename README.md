# RTDL

RTDL is a Python-hosted ray-tracing DSL/runtime for non-graphical workloads:
spatial search, graph-adjacent visibility, nearest-neighbor screening,
simulation collision checks, and database-style summaries.

The core idea is simple: write app-shaped Python code, lower the traversal-heavy
part to an RT-capable backend, then keep the remaining app logic explicit. RTDL
owns traversal, candidate generation, row plumbing, and selected native
continuations where they are documented. Python still owns orchestration,
ranking, refinement, clustering, force reduction, SQL-style output assembly, and
other non-RT phases unless a page says otherwise.

The current released version is `v0.9.8`.
- current released version: `v0.9.8`

## Start Fast

```bash
python3 -m pip install -e .
PYTHONPATH=src:. python examples/rtdl_hello_world.py
PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend embree
```

Read next:

- [Public Documentation Map](docs/public_documentation_map.md)
- [Docs Index](docs/README.md)
- [Quick Tutorial](docs/quick_tutorial.md)
- [App And Example Quickstart](docs/app_example_quickstart.md)
- [Application Catalog](docs/application_catalog.md)
- [v1.0 App Acceleration Inventory](docs/v1_0_app_acceleration_inventory.md)
- [Performance Model](docs/performance_model.md)
- [v1.0 RTX App Status](docs/v1_0_rtx_app_status.md)

## Current Status

| Area | State |
| --- | --- |
| Release | current released version: `v0.9.8` |
| v1.0 mainline | app-shaped RTDL proof, documentation, and bounded evidence |
| Public RTX wording | `12 reviewed` bounded RTX sub-path rows after Goal1224 |
| Still blocked | `graph_analytics`, `polygon_pair_overlap_area_rows` public speedup wording |
| Not yet public-reviewed | `database_analytics`, `polygon_set_jaccard` public speedup wording |
| Non-NVIDIA proof lines | HIPRT, Vulkan, and Apple RT prove selected backend surfaces, but are not the v1.0 NVIDIA RTX evidence path |

RTDL is not a renderer or graphics engine. It uses ray-tracing-style
acceleration structures and traversal for application kernels.

## v1.0 Direction

v1.0 is for proving that a Python-hosted RT DSL works on real
application-shaped workloads. It is allowed to use app-specific engine
customization where needed to make supported apps measurable and useful. That is
v1.0 proof machinery, not the final architecture.

v1.5 is planned to replace app-specific engine customization with reviewed
generic traversal-plus-reduction primitives. v2.0 targets broader end-to-end performance through explicit zero-copy partnership with GPU compute tools for
the non-RT phases.

The practical v1.0 rule: RT traversal can be fast while the full app is still
limited by Python continuation, exact refinement, ranking, clustering, SQL-style
materialization, graph analytics, or force reduction.

## NVIDIA RT-Core Claim Boundary

`--backend optix` means an app selected an OptiX-capable execution path. It is
not, by itself, a public claim that NVIDIA RT cores accelerated the app. Public
RTX wording requires `--require-rt-core`, valid same-contract evidence, and a
saved review trail.

Front-page rules:

- Claim the exact reviewed prepared/native sub-path, not the whole app.
- Do not generalize from one OptiX mode to all OptiX modes.
- Do not count Python post-processing, exact polygon refinement, SQL/DBMS
  behavior, ANN ranking, DBSCAN expansion, graph-system analytics, or
  Barnes-Hut force reduction unless a later review explicitly authorizes it.
- Treat the support matrix and v1.0 inventory as the authority for current
  wording.

Reviewed rows are bounded public sub-path wording, not automatic public speedup claims.
Each line is not a whole-app, default-mode, Python-postprocess, or broad RT-core acceleration claim.

Key examples of the boundary:

- Robot collision: `prepared_pose_flags` is normalized per-pose wording only,
  not a same-total-work wall-time claim and not a whole-app robot-planning
  claim; witness-row output remains outside the wording.
- Barnes-Hut: node coverage can be reviewed; force-vector computation and
  opening-rule work remain outside.
- Facility KNN and road hazard: reviewed prepared/compact-summary sub-paths do
  not authorize ranked assignment, GIS routing, or full application claims.
- Claim-sensitive prepared summary modes include `rt_count_threshold_prepared`
  and `rt_core_flags_prepared`; they are scalar threshold/core-flag phases, not
  whole outlier-detection or DBSCAN claims.
- Graph, DB, polygon, ANN, DBSCAN, and Hausdorff docs must be read through the
  support matrix before publishing performance wording.
- prepared road hazard, prepared native hit-count traversal, and Hausdorff exact distance
  wording all stay bounded by the status page and support matrix.

Goal748 is the robot OptiX short-ray erratum boundary: pre-Goal748 robot OptiX
evidence used a short-ray `optixReportIntersection` path later fixed by
Goal748. Use post-fix Goal748 or later robot OptiX evidence for current robot
claims.

Goal1177 is recovered clean-source RTX A5000 evidence for external-review input only.
Goal1184 records Goal1182 RTX A4500 batch evidence as external-review input only.
Neither goal adds a new reviewed public wording row or authorizes public speedup wording.
Goal1177 does not authorize public speedup wording. Goal1177 does not add a new reviewed public wording row.

Detailed evidence and review trail:

- [v1.0 RTX App Status](docs/v1_0_rtx_app_status.md)
- [v1.0 App Acceleration Inventory](docs/v1_0_app_acceleration_inventory.md)
- [App Engine Support Matrix](docs/app_engine_support_matrix.md)
- [Performance Model](docs/performance_model.md)
- [RTX Wording Resolution Consensus](docs/reports/goal1224_two_ai_consensus_2026-05-01.md)
- [RTX Wording Resolution Consensus Alias](docs/reports/goal1224_two_ai_rtx_wording_resolution_consensus_2026-05-01.md)

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
- [RTDL v0.9.5 Release Package](docs/release_reports/v0_9_5/README.md)
- [RTDL v0.8 Release Package](docs/release_reports/v0_8/README.md)
- [RTDL v0.8 Release Statement](docs/release_reports/v0_8/release_statement.md)
- [RTDL v0.8 Support Matrix](docs/release_reports/v0_8/support_matrix.md)
- [RTDL Current Main Support Matrix](docs/current_main_support_matrix.md)
- [Engine Feature Support Contract](docs/features/engine_support_matrix.md)
- [RTDL v0.8 App Building Tutorial](docs/tutorials/v0_8_app_building.md)
- [Hausdorff Linux Performance Evidence](docs/reports/goal507_hausdorff_linux_perf_report_2026-04-17.md)
- [Robot/Barnes-Hut Linux Performance Evidence](docs/reports/goal509_robot_barnes_linux_perf_report_2026-04-17.md)
- [Goal524 v0.8 Stage-1 Proximity Linux Performance](docs/reports/goal524_v0_8_stage1_proximity_linux_perf_2026-04-17.md)

RTX-class
      performance validation remains bounded to reviewed prepared/native
sub-paths. Earlier Linux Goal509 evidence covered the hit-count formulation,
Embree, and pre-fix OptiX; new backend speedup claims need fresh gates and
should use the post-fix Goal748 parity/performance report for robot OptiX.
Barnes-Hut now has bounded Linux CPU/Embree/OptiX/Vulkan candidate-generation
evidence that stays separate from Python opening-rule and force-reduction work.

For legacy guardrails: earlier Linux Goal509 evidence covered the hit-count formulation.

`v0.9.5`: earlier public release for bounded any-hit, visibility rows, and
Python-side emitted-row reductions. The released `v0.8.0` app-building examples
include `examples/rtdl_hausdorff_distance_app.py`,
`examples/rtdl_ann_candidate_app.py`, `examples/rtdl_outlier_detection_app.py`,
`examples/rtdl_dbscan_clustering_app.py`,
`examples/rtdl_robot_collision_screening_app.py`,
`examples/rtdl_barnes_hut_force_app.py`,
`examples/rtdl_database_analytics_app.py`, and
`examples/rtdl_apple_rt_demo_app.py`. These apps use existing RTDL features and
Python-owned application logic; they are not a new released backend/language
surface.

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
