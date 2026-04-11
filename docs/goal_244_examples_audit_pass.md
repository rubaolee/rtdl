# Goal 244: Examples Audit Pass

## Objective

Record the next system-audit pass for the examples tier after the front page,
tutorial, and public docs tiers.

## Scope

This pass focuses on the main release-facing example surface:

- `examples/README.md`
- `examples/rtdl_hello_world.py`
- `examples/rtdl_hello_world_backends.py`
- `examples/rtdl_fixed_radius_neighbors.py`
- `examples/rtdl_knn_rows.py`
- `examples/rtdl_segment_polygon_hitcount.py`
- `examples/rtdl_segment_polygon_anyhit_rows.py`
- `examples/rtdl_service_coverage_gaps.py`
- `examples/rtdl_event_hotspot_screening.py`
- `examples/rtdl_facility_knn_assignment.py`
- `examples/visual_demo/rtdl_lit_ball_demo.py`

## Required Checks

- fresh-clone style execution does not depend on hidden maintainer setup
- public backend choices match the docs
- output shapes remain understandable and stable
- the example index clearly separates release-facing material from preserved
  internal or generated artifacts
