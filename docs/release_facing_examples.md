# Release-Facing Example Command Archive

Status: current v2.0 source-tree command archive.

This page is for reviewers who need a compact command list for the public
example surface. If you are learning RTDL for the first time, start with:

- [Learn RTDL](learn/README.md)
- [Quick Tutorial](quick_tutorial.md)
- [Tutorial Ladder](tutorials/README.md)
- [App And Example Quickstart](app_example_quickstart.md)
- [Examples Index](../examples/README.md)

Run examples from the repository root with `PYTHONPATH=src:.`.

## Current Support Links

- [Application Catalog](application_catalog.md)
- [App Engine Support Matrix](app_engine_support_matrix.md)
- [Current Support Matrix](current_main_support_matrix.md)
- [Performance Model](performance_model.md)
- [Partner Acceleration Boundaries](partner_acceleration_boundaries.md)

## Portable First Runs

```bash
PYTHONPATH=src:. python examples/rtdl_hello_world.py
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_feature_quickstart_cookbook.py
```

## App Examples

```bash
PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_ann_candidate_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_outlier_detection_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_dbscan_clustering_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_robot_collision_screening_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_barnes_hut_force_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_graph_analytics_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_database_analytics_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_road_hazard_screening.py --backend cpu_python_reference
```

## Embree And OptiX Examples

Build native libraries before using native backends:

```bash
make build-embree
make build-optix
```

Then use the app's documented backend flags:

```bash
PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend embree
PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend optix
PYTHONPATH=src:. python examples/rtdl_segment_polygon_anyhit_rows.py --backend embree --output-mode segment_counts
PYTHONPATH=src:. python examples/rtdl_segment_polygon_anyhit_rows.py --backend optix --output-mode segment_counts
PYTHONPATH=src:. python examples/rtdl_polygon_pair_overlap_area_rows.py --backend embree --output-mode summary
PYTHONPATH=src:. python examples/rtdl_polygon_pair_overlap_area_rows.py --backend optix --output-mode summary
```

## Partner Candidate Examples

```bash
PYTHONPATH=src:. python examples/rtdl_partner_anyhit.py --partner numpy --backend embree
PYTHONPATH=src:. python examples/rtdl_partner_anyhit.py --partner cupy --backend optix
```

Partner commands are part of the v2.0 pre-release candidate surface. They do
not imply arbitrary PyTorch/CuPy acceleration, package-install support, or a
final release.

## Claim Boundary

`--backend optix` is a backend-selection flag, not an automatic NVIDIA RT-core
performance claim. Public wording must name the exact app, backend, partner,
hardware, command shape, output contract, and artifact.

Older command archives and old release-specific example notes live under:

- [Audit Door](audit/README.md)
- [Root Archive](history/root_archive/README.md)
- [Release Reports](release_reports/)
- [Benchmark And Audit Reports](reports/)
