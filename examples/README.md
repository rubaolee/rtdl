# Examples

This directory contains two kinds of material:

- release-facing examples you can run first
- internal or historical development artifacts that are kept for auditability

## Start Here

If you are new to RTDL, use these files first:

- `rtdl_hello_world.py`
- `rtdl_hello_world_backends.py`
- `rtdl_segment_polygon_hitcount.py`
- `rtdl_segment_polygon_anyhit_rows.py`
- `rtdl_polygon_pair_overlap_area_rows.py`
- `rtdl_polygon_set_jaccard.py`
- `rtdl_road_hazard_screening.py`
- `visual_demo/rtdl_lit_ball_demo.py`
- `visual_demo/rtdl_smooth_camera_orbit_demo.py`

## Internal And Historical Artifacts

Files under `internal/` are preserved for development history, evaluation, or
LLM-authoring experiments. They are not the primary release-facing entry
points for external users.

The internal reference kernels used by tests and some implementation code are:

- `rtdl_goal10_reference.py`
- `rtdl_release_reference.py`

For release-facing examples and commands, prefer the docs entry points:

- `../README.md`
- `../docs/quick_tutorial.md`
- `../docs/release_facing_examples.md`
