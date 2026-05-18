# RTDL Examples

This directory is organized for RTDL v2.0 users first.  Start in
`v2_0/`, then choose by purpose: first run, feature, full app, partner
continuation, or research benchmark.

Run examples from the repository root with source-tree usage:

```bash
PYTHONPATH=src:. python examples/v2_0/getting_started/rtdl_hello_world.py
```

## Start Here

| Purpose | Directory | First command |
| --- | --- | --- |
| First runnable RTDL programs | `v2_0/getting_started/` | `PYTHONPATH=src:. python examples/v2_0/getting_started/rtdl_hello_world.py` |
| Individual feature examples | `v2_0/features/` | `PYTHONPATH=src:. python examples/v2_0/features/ray_queries/rtdl_ray_triangle_any_hit.py` |
| Complete v2.0 applications | `v2_0/apps/` | `PYTHONPATH=src:. python examples/v2_0/apps/ml/rtdl_outlier_detection_app.py --backend cpu_python_reference` |
| Partner continuation examples | `v2_0/partners/` | `PYTHONPATH=src:. python examples/v2_0/partners/rtdl_partner_anyhit.py --partner numpy --backend embree` |
| Paper-facing performance studies | `v2_0/research_benchmarks/` | read the benchmark README before running |

## Directory Map

| Directory | Audience | Contents |
| --- | --- | --- |
| `v2_0/getting_started/` | New learner | Hello world, backend selection, feature cookbook |
| `v2_0/features/` | User learning one RTDL primitive family | Ray queries, neighbors, database reductions, graph traversal, spatial rows |
| `v2_0/apps/` | User building an application | Analytics, geospatial, ML, robotics, simulation, trajectory examples |
| `v2_0/partners/` | Advanced user | NumPy/CuPy/user-owned continuation examples around RTDL outputs |
| `v2_0/research_benchmarks/hausdorff_xhd/` | Research/performance reader | Hausdorff/X-HD-inspired RTDL study and benchmark harnesses |
| `v2_0/research_benchmarks/spatial_rayjoin/` | Research/performance reader | RayJoin-inspired spatial join study |
| `legacy_or_backend_proofs/` | Backend maintainer | Backend proof demos that are not the first learner path |
| `visual_demo/` | Visual demo reader | Rendering/visual query demos |
| `reference/` | Test/doc maintainer | Canonical reference kernels used by docs and tests |
| `generated/` | Auditor | Preserved generated bundles |
| `internal/` | Maintainer | Historical/internal development artifacts |

## v2.0 Feature Families

| Feature family | Directory |
| --- | --- |
| Ray queries and row reductions | `v2_0/features/ray_queries/` |
| Fixed-radius and KNN rows | `v2_0/features/neighbors/` |
| Columnar database scans and grouped reductions | `v2_0/features/database/` |
| Graph traversal and triangle counting | `v2_0/features/graph/` |
| Segment/polygon and polygon-set spatial rows | `v2_0/features/spatial/` |

## Important Performance Applications

| Study | Directory | Boundary |
| --- | --- | --- |
| Hausdorff vs X-HD-style baselines | `v2_0/research_benchmarks/hausdorff_xhd/` | Serious RTDL language/runtime study, not a claim that every Hausdorff input beats every CUDA implementation |
| Spatial joins vs RayJoin-style baselines | `v2_0/research_benchmarks/spatial_rayjoin/` | Serious RTDL spatial-query study, not a claim that RTDL reproduces every RayJoin paper result |

## Compatibility

Older imports such as `from examples import rtdl_hello_world` are kept through a
lazy compatibility map in `examples/__init__.py`.  New documentation should use
the explicit `examples/v2_0/...` paths.

## Claim Boundaries

- `--backend optix` is not by itself a broad NVIDIA RT-core speedup claim.
- Partner examples show user-owned continuation around RTDL outputs; RTDL does
  not claim to accelerate arbitrary NumPy, PyTorch, or CuPy programs.
- `legacy_or_backend_proofs/`, `generated/`, `reference/`, and `internal/` are
  not first-run learner directories.

For guided learning and support boundaries, prefer:

- [Project Front Page](../README.md)
- [Docs Index](../docs/README.md)
- [Tutorial Ladder](../docs/tutorials/README.md)
- [App And Example Quickstart](../docs/app_example_quickstart.md)
- [Application Catalog](../docs/application_catalog.md)
- [App Engine Support Matrix](../docs/app_engine_support_matrix.md)
- [Performance Model](../docs/performance_model.md)

Selecting `--backend optix` does not automatically make a public RT-core
speedup claim; use the support matrix and reviewed evidence before publishing
performance wording.
