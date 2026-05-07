# RTDL

RTDL is a Python-hosted ray-tracing DSL/runtime for non-graphical workloads:
spatial search, visibility, nearest-neighbor screening, collision checks, and
database-style summaries.

The core idea: write app-shaped Python code, lower the traversal-heavy part to
an RT-capable backend, and keep the remaining app logic explicit.

The current released version is `v1.5`.

## Start Fast

```bash
PYTHONPATH=src:. python examples/rtdl_hello_world.py
PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend embree
```

RTDL v1.5 is used directly from the source tree. Keep `PYTHONPATH=src:.` in
front of example and test commands unless a later packaged release adds
installation metadata.

## Read Next

- [Public Documentation Map](docs/public_documentation_map.md)
- [Docs Index](docs/README.md)
- [Quick Tutorial](docs/quick_tutorial.md)
- [App And Example Quickstart](docs/app_example_quickstart.md)
- [Application Catalog](docs/application_catalog.md)
- [v1.0 App Acceleration Inventory](docs/v1_0_app_acceleration_inventory.md)
- [v1.5 Release Package](docs/release_reports/v1_5/README.md)
- [v1.5.1 COLLECT_K_BOUNDED Candidate Docs](docs/release_reports/v1_5_1/README.md)
- [v1.1 OptiX/Embree Status](docs/v1_1_optix_status.md)
- [Current Main Support Matrix](docs/current_main_support_matrix.md)
- [Engine Feature Support Contract](docs/features/engine_support_matrix.md)
- [Performance Model](docs/performance_model.md)
- [IR And Lowering](docs/rtdl/ir_and_lowering.md)

## Current Status

| Area | State |
| --- | --- |
| Release | current released version: `v1.5` |
| v1.5 | released standalone Embree+OptiX language/runtime completion for the supported surface |
| v1.5.1 candidate docs | `COLLECT_K_BOUNDED` documented experimental public-candidate; not stable primitive promotion, no public speedup wording, no zero-copy wording, no whole-app claims, and no release tag action |
| v1.0 | released app-shaped RTDL proof, documentation, and bounded evidence |
| Current main | post-v1.5 integration branch; do not infer broader claims than the v1.5 release package allows |
| v1.1 OptiX evidence | `polygon_pair_overlap_area_rows` has bounded 3-AI-reviewed positive wording |
| Still not public speedup-ready | whole-app graph/DB/polygon claims, Jaccard speedup wording, and non-RT continuations such as ranking, clustering, graph analytics, SQL-style materialization, and force reduction |

RTDL is not a renderer or graphics engine. It uses ray-tracing-style
acceleration structures and traversal for application kernels.

## Roadmap Boundary

v1.0 is for proving that a Python-hosted RT DSL works on real app-shaped
workloads. It may use app-specific engine customization where needed to make
supported apps measurable and useful. That is v1.0 proof machinery, not the final architecture.

v1.1 through v1.4 are internal engineering milestones on `main`, not public
release packages or tags. They harden Embree/OptiX evidence, push NVIDIA RT
performance, define the primitive ABI/parity contracts, and migrate the first
compatibility wrappers.

v1.5 is the released standalone Embree+OptiX language/runtime completion for
the supported surface. It covers 14 included app contracts, 4 excluded rows,
and stable generic traversal-plus-reduction primitives. It is not a whole-app
speedup claim and not a zero-app-knowledge native-engine release: some native
Embree/OptiX entry points remain workload-shaped compatibility/proof surfaces.
v1.5.1 is the `COLLECT_K_BOUNDED` promotion track; v2.0 targets broader
end-to-end performance through explicit partner mechanisms for non-RT phases.

The practical v1.0 rule: RT traversal can be fast while the full app is still
limited by Python continuation, exact refinement, ranking, clustering,
SQL-style materialization, graph analytics, or force reduction.

## NVIDIA RT-Core Claim Boundary

`--backend optix` is not, by itself, a public claim that NVIDIA RT cores accelerated the app.
Use `--require-rt-core` only for documented, reviewed claim-sensitive modes.

Front-page rules:

- Claim the exact reviewed prepared/native sub-path, not the whole app.
- Do not generalize from one OptiX mode to all OptiX modes.
- Do not count Python post-processing, exact polygon refinement, SQL/DBMS
  behavior, ANN ranking, DBSCAN expansion, graph-system analytics, or
  Barnes-Hut force reduction unless a later review explicitly authorizes it.
- Treat the v1.5 release package/support matrix as the current release
  authority, with the v1.0 inventory preserved for app-boundary history.
- Reviewed rows are bounded public sub-path wording, not automatic public speedup claims; each line is not a whole-app, default-mode, Python-postprocess, or broad RT-core acceleration claim.

Detailed evidence and review trail:

- [v1.0 RTX App Status](docs/v1_0_rtx_app_status.md)
- [v1.1 OptiX/Embree Status](docs/v1_1_optix_status.md)
- [v1.0 App Acceleration Inventory](docs/v1_0_app_acceleration_inventory.md)
- [App Engine Support Matrix](docs/app_engine_support_matrix.md)
- [Performance Model](docs/performance_model.md)

## What RTDL Contains

| Capability | Public shape |
| --- | --- |
| Geometry rows | `knn_rows`, `bounded_knn_rows`, `fixed_radius_neighbors`, closest-hit paths |
| Any-hit traversal | `ray_triangle_any_hit`, `visibility_rows`, prepared repeated-query visibility/count helpers |
| Reductions | `reduce_rows` in Python plus v1.5 stable app-name-free summary/reduction primitives where documented |
| IR and lowering | `CompiledKernel` lowers to `RTExecutionPlan` |
| Backends | CPU reference, Embree, OptiX, HIPRT, Vulkan, Apple RT/MPS RT where documented |
| Apps | Hausdorff, ANN candidate search, outlier detection, DBSCAN, robot screening, Barnes-Hut, graph visibility, DB summaries, road hazard, segment/polygon summaries |

`ray_triangle_any_hit`, `visibility_rows`, and `reduce_rows` are public RTDL
surfaces. OptiX, Embree, and HIPRT have native early-exit any-hit support in
the released line. Vulkan and Apple RT support selected any-hit/visibility
contracts, but some paths are not a native reduction or public speedup claim.

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
