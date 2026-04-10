# Release-Facing Examples

This page is the canonical example index for the frozen RTDL `v0.2` surface
and the active RTDL `v0.4` nearest-neighbor preview line.

Use these first if you want the examples that best match the current accepted
live workload/package story.

Before running any command below:

- clone the repo with `git clone https://github.com/rubaolee/rtdl.git`
- enter the checkout with `cd rtdl`
- keep the `PYTHONPATH=src:.` prefix so Python imports the local `rtdsl`
  package from `src/rtdsl/`

## v0.4 nearest-neighbor preview examples

These are the current release-facing examples for the active `v0.4` line.
They are correctness-first nearest-neighbor examples, not a released benchmark
claim yet.

### Fixed-Radius Neighbors

- code:
  - [rtdl_fixed_radius_neighbors.py](../examples/rtdl_fixed_radius_neighbors.py)
- run:

```bash
cd rtdl
PYTHONPATH=src:. python3 examples/rtdl_fixed_radius_neighbors.py --backend cpu_python_reference
```

### K-Nearest-Neighbor Rows

- code:
  - [rtdl_knn_rows.py](../examples/rtdl_knn_rows.py)
- run:

```bash
cd rtdl
PYTHONPATH=src:. python3 examples/rtdl_knn_rows.py --backend cpu_python_reference
```

If Embree is available locally, both examples also support:

```bash
cd rtdl
PYTHONPATH=src:. python3 examples/rtdl_fixed_radius_neighbors.py --backend embree
PYTHONPATH=src:. python3 examples/rtdl_knn_rows.py --backend embree
```

## Core examples

### Segment/Polygon Hit Count

- code:
  - [rtdl_segment_polygon_hitcount.py](../examples/rtdl_segment_polygon_hitcount.py)
- run:

```bash
cd rtdl
PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
```

### Segment/Polygon Any-Hit Rows

- code:
  - [rtdl_segment_polygon_anyhit_rows.py](../examples/rtdl_segment_polygon_anyhit_rows.py)
- run:

```bash
cd rtdl
PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_anyhit_rows.py --backend cpu_python_reference --copies 16
```

### Polygon-Set Jaccard

- code:
  - [rtdl_polygon_set_jaccard.py](../examples/rtdl_polygon_set_jaccard.py)
- run:

```bash
cd rtdl
PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py
```

### Polygon-Pair Overlap Area Rows

- code:
  - [rtdl_polygon_pair_overlap_area_rows.py](../examples/rtdl_polygon_pair_overlap_area_rows.py)
- run:

```bash
cd rtdl
PYTHONPATH=src:. python3 examples/rtdl_polygon_pair_overlap_area_rows.py
```

## App-style example

- [rtdl_road_hazard_screening.py](../examples/rtdl_road_hazard_screening.py)

This is the best short example of how the segment/polygon line looks in a more
user-facing workflow.

## RTDL Plus Python App Demo

Primary 3D demo source:

- [rtdl_hidden_star_stable_ball_demo.py](../examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py)

This is the current main 3D RTDL-plus-Python demo source. RTDL handles both:

- primary camera hit queries
- shadow visibility queries

Python still owns the surrounding application layer: animation, shading,
background, and frame output.

Primary hidden-star stable 3D demo sanity check:

```bash
cd rtdl
PYTHONPATH=src:. python3 examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py --backend cpu_python_reference --compare-backend none --width 48 --height 48 --latitude-bands 6 --longitude-bands 12 --frames 1 --jobs 1 --shadow-mode rtdl_light_to_surface --output-dir build/quick_hidden_star_demo
```

Secondary smaller app demo:

- [rtdl_lit_ball_demo.py](../examples/visual_demo/rtdl_lit_ball_demo.py)

This is a small user-authored RTDL-plus-Python application. RTDL handles the
ray/triangle hit relationships. Python handles the visible-span recovery,
brightness calculation, ASCII preview, and `.pgm` image output.

The visual-demo scripts create the output directory automatically when needed,
so an empty fresh clone does not need a pre-existing `build/` directory.

Run:

```bash
cd rtdl
PYTHONPATH=src:. python3 examples/visual_demo/rtdl_lit_ball_demo.py --backend cpu_python_reference --compare-backend none --width 240 --height 240 --triangles 512 --output build/rtdl_lit_ball_demo_hq.pgm
```

Small first sanity check for the smoother comparison line:

```bash
cd rtdl
PYTHONPATH=src:. python3 examples/visual_demo/rtdl_smooth_camera_orbit_demo.py --backend cpu_python_reference --compare-backend none --width 48 --height 48 --latitude-bands 6 --longitude-bands 12 --frames 1 --jobs 1 --output-dir build/quick_smooth_camera_demo
```

Important boundary:

- this is a user-level RTDL-plus-Python application demo
- it is not a claim that RTDL v0.2.0 is a full rendering system

## Generate-only entry point

- script:
  - [rtdl_generate_only.py](../scripts/rtdl_generate_only.py)

Current accepted narrow generate-only example:

```bash
cd rtdl
PYTHONPATH=src:. python3 scripts/rtdl_generate_only.py --workload polygon_set_jaccard --dataset authored_polygon_set_jaccard_minimal --backend cpu_python_reference --output-mode rows --artifact-shape handoff_bundle --output build/generated_polygon_set_jaccard_bundle
```

The repo also preserves example generated output under:

- [examples/generated/](../examples/generated/README.md)

Those files are useful for inspection and handoff workflows, but they are not
the main first-run entry points for new users.

## Notes

- these are the release-facing examples for the frozen v0.2 scope
- if you cloned the repo as `rtdl`, every command above is intended to work
  from that clone root
- older demos and exploratory examples still exist in the repo, but they are
  not the primary release-facing entry points
