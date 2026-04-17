# Examples

This directory contains two kinds of material:

- release-facing examples you can run first
- reference kernels and helper generators used by examples and tests
- preserved generated bundles and generated example output
- internal or historical development artifacts that are kept for auditability

## Start Here

If you are new to RTDL, use these files first:

- `rtdl_hello_world.py`
- `rtdl_hello_world_backends.py`
- `rtdl_fixed_radius_neighbors.py`
- `rtdl_knn_rows.py`
- `rtdl_graph_bfs.py`
- `rtdl_graph_triangle_count.py`
- `rtdl_db_conjunctive_scan.py`
- `rtdl_db_grouped_count.py`
- `rtdl_db_grouped_sum.py`
- `rtdl_v0_7_db_app_demo.py`
- `rtdl_v0_7_db_kernel_app_demo.py`
- `rtdl_sales_risk_screening.py`
- `rtdl_service_coverage_gaps.py`
- `rtdl_event_hotspot_screening.py`
- `rtdl_facility_knn_assignment.py`
- `rtdl_segment_polygon_hitcount.py`
- `rtdl_segment_polygon_anyhit_rows.py`
- `rtdl_polygon_pair_overlap_area_rows.py`
- `rtdl_polygon_set_jaccard.py`
- `rtdl_road_hazard_screening.py`
- `visual_demo/rtdl_lit_ball_demo.py`
- `visual_demo/rtdl_hidden_star_stable_ball_demo.py`
- `visual_demo/render_hidden_star_chunked_video.py`

## Reference Material

Files under `reference/` contain canonical kernels and helper generators used
by examples, tests, and bounded evaluation paths.

## Generated Material

Files under `generated/` are preserved generated output artifacts. They are
useful for inspection and handoff workflows, but they are not the primary
release-facing start points for new users.

## Internal And Historical Artifacts

Files under `internal/` are preserved for development history, evaluation, or
LLM-authoring experiments. They are not the primary release-facing entry
points for external users.

For release-facing examples and commands, prefer the docs entry points:

- `../README.md`
- `../docs/quick_tutorial.md`
- `../docs/tutorials/README.md`
- `../docs/release_facing_examples.md`

Current DB example boundary:

- examples expose:
  - `cpu_python_reference`
  - `cpu`
  - `embree`
  - `optix`
  - `vulkan`
- `rtdl_v0_7_db_app_demo.py` is the app-level demo: it shows one
  denormalized order table becoming matched row IDs, grouped counts, and
  grouped sums through the v0.7 bounded DB workload surface
- `rtdl_v0_7_db_kernel_app_demo.py` is the kernel-form companion demo: it
  shows `rt.input(..., role="probe")`, `rt.input(..., role="build")`,
  `rt.traverse(..., accel="bvh")`, `rt.refine(...)`, and `rt.emit(...)` around
  the same bounded DB workload surface
- PostgreSQL remains a Linux correctness/performance anchor, not a public
  example backend flag
