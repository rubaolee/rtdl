# RTDL Examples

This directory is organized for current RTDL users first. Start in
`current/`, then choose by purpose: first run, feature, full app, partner
continuation, or research benchmark.

The `current/` tree contains the learner-facing examples retained by RTDL 3.0.
Historical examples, generated bundles,
backend proofs, and internal development artifacts live under `history/`
rather than in the first-run examples path.

Run examples from the repository root with source-tree usage:

```bash
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
```

Start with the static V3 canonical-mapping example. Use the portable reference
examples to learn data contracts, then configure OptiX for the NVIDIA V3
execution path.

For a full Linux/pod smoke run across tutorials, examples, demos, and benchmark
front doors, install the native/runtime prerequisites first:

```bash
apt-get install -y libgeos-dev pkg-config libembree-dev
python -m pip install numpy pillow imageio imageio-ffmpeg  # Dependency install only; this does not install RTDL
```

If system Python is externally managed, create a virtual environment and run
the same `pip` command inside it.

## Start Here

| Purpose | Directory | First command |
| --- | --- | --- |
| First runnable RTDL programs | `current/getting_started/` | `PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py` |
| Primitive discovery workflow | `current/getting_started/` | `PYTHONPATH=src:. python examples/current/getting_started/rtdl_primitive_discovery_workflow.py` |
| Individual feature examples | `current/features/` | `PYTHONPATH=src:. python examples/current/features/ray_queries/rtdl_ray_triangle_any_hit.py` |
| Complete current applications | `current/apps/` | `PYTHONPATH=src:. python examples/current/apps/ml/rtdl_outlier_detection_app.py --backend cpu_python_reference` |
| Partner continuation examples | `current/partners/` | `PYTHONPATH=src:. python examples/current/partners/rtdl_partner_anyhit.py --partner numpy --backend embree` |
| Demoted or design-pressure learner apps | `current/learner_apps/` | read the learner-app README before treating any result as performance evidence |
| Paper-facing performance studies | `current/research_benchmarks/` | read the benchmark README before running |

## Directory Map

| Directory | Audience | Contents |
| --- | --- | --- |
| `current/getting_started/` | New learner | Hello world, backend selection, primitive discovery, feature cookbook |
| `current/features/` | User learning one RTDL primitive family | Ray queries, neighbors, database reductions, graph traversal, spatial rows |
| `current/apps/` | User building an application | Analytics, geospatial, ML, robotics, simulation, trajectory examples |
| `current/partners/` | Advanced user | NumPy/CuPy/Numba/user-owned continuation examples around RTDL outputs |
| `current/learner_apps/` | Learner/research reader | Demoted or design-pressure app-scale examples that are not benchmark claims |
| `current/research_benchmarks/hausdorff_xhd/` | Research/performance reader | Hausdorff/X-HD-inspired RTDL study and benchmark harnesses |
| `current/research_benchmarks/spatial_rayjoin/` | Research/performance reader | RayJoin-inspired spatial join study |
| `visual_demo/` | Visual demo reader | Rendering/visual query demos |
| `reference/` | Test/doc maintainer | Canonical reference kernels used by docs, examples, and tests; not the first learner path |

## Feature Families

| Feature family | Directory |
| --- | --- |
| Ray queries and row reductions | `current/features/ray_queries/` |
| Fixed-radius and KNN rows | `current/features/neighbors/` |
| Columnar database scans and grouped reductions | `current/features/database/` |
| Graph traversal and triangle counting | `current/features/graph/` |
| Segment/polygon and polygon-set spatial rows | `current/features/spatial/` |

## Important Performance Applications

| Study | Directory | Boundary |
| --- | --- | --- |
| Hausdorff vs X-HD-style baselines | `current/research_benchmarks/hausdorff_xhd/` | Serious RTDL language/runtime study, not a claim that every Hausdorff input beats every CUDA implementation |
| Spatial joins vs RayJoin-style baselines | `current/research_benchmarks/spatial_rayjoin/` | Serious RTDL spatial-query study, not a claim that RTDL reproduces every RayJoin paper result |
| RT-DBSCAN-style neighbor clustering | `current/research_benchmarks/rt_dbscan/` | Serious fixed-radius/component study over generic primitives, not a DBSCAN-native engine ABI |
| Robot collision screening | `current/research_benchmarks/robot_collision/` | Prepared static-scene screening study, not a planner or swept-collision solver |
| RayDB-style grouped aggregates | `current/research_benchmarks/raydb_style/` | Columnar grouped-reduction study, not SQL, SSB, or a DBMS |
| Barnes-Hut / RT-BarnesHut-style | `current/research_benchmarks/barnes_hut/` | Hierarchical aggregate-frontier study, not an app-specific force primitive |
| LibRTS-style spatial index | `current/research_benchmarks/librts_spatial_index/` | Generic AABB point/range count study, not full mutable LibRTS reproduction |
| RTNN neighbor search | `current/research_benchmarks/rtnn/` | Serious neighbor-search study over generic prepared fixed-radius and partner top-k contracts, not a full RTNN paper reproduction or ANN-index claim |
| Triangle counting | `current/research_benchmarks/triangle_counting/` | RT-Graph/SIGMETRICS 2025 target; single-contract graph benchmark with accepted segmented/streamed-lowering limitation |

## Demoted Research/Learner Apps

| App | Directory | Boundary |
| --- | --- | --- |
| GPU-RMQ | `current/learner_apps/gpu_rmq/` | Learner/design-pressure app; useful for primitive design pressure, not a benchmark app or speedup claim |

## Compatibility

Older imports such as `from examples import rtdl_hello_world` are kept through a
lazy compatibility map in `examples/__init__.py`.  New documentation should use
the explicit `examples/current/...` paths.

## Claim Boundaries

- Short canonical boundary page:
  [Current Claim Boundaries](../docs/learn/current_claim_boundaries.md).
- `--backend optix` is not by itself a broad NVIDIA RT-core speedup claim.
- Partner examples show user-owned continuation around RTDL outputs; RTDL does
  not claim to accelerate arbitrary NumPy, CuPy, Numba, or user-owned extension
  programs.
- `reference/` is support code for current examples and tests, not the first-run
  learner directory.
- Historical generated examples, backend proof demos, and internal examples are
  archived under `../history/examples_internal/`.

For guided learning and support boundaries, prefer:

- [Project Front Page](../README.md)
- [Docs Index](../docs/README.md)
- [Tutorials](../tutorials/README.md)
- [Current Tutorial Track](../tutorials/current/README.md)
- [App And Example Quickstart](../docs/app_example_quickstart.md)
- [Application Catalog](../docs/application_catalog.md)
- [Choosing A Partner For Custom Logic](../docs/learn/partner_choice_for_custom_logic.md)
- [Benchmark Partner Reference Matrix](../docs/learn/benchmark_partner_reference_matrix.md)
- [Current Support Matrix](../docs/current_main_support_matrix.md)
- [App Engine Support Matrix](../docs/app_engine_support_matrix.md)
- [Performance Model](../docs/performance_model.md)

Selecting `--backend optix` does not automatically make a public RT-core
speedup claim; use the support matrix and reviewed evidence before publishing
performance wording.
