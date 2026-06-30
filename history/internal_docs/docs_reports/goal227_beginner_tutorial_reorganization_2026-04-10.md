# Goal 227 Report: Beginner Tutorial Reorganization (2026-04-10)

## Scope

This slice reorganizes the beginner-facing tutorial surface into a guided
learning ladder instead of a flat collection of pages.

Files added:

- `docs/tutorials/README.md`
- `docs/tutorials/hello_world.md`
- `docs/tutorials/sorting_demo.md`
- `docs/tutorials/segment_polygon_workloads.md`
- `docs/tutorials/nearest_neighbor_workloads.md`
- `docs/tutorials/rendering_and_visual_demos.md`

Files rewritten/updated:

- `docs/quick_tutorial.md`
- `docs/README.md`
- `docs/release_facing_examples.md`
- `examples/README.md`

## Design

The new beginner path is:

1. first run
2. hello world
3. sorting demo
4. released workload families
5. active nearest-neighbor preview workloads
6. RTDL-plus-Python rendering demos

This solves two previous usability problems:

- beginners had to infer the learning order themselves
- the sorting and rendering lines existed, but did not have an honest place in
  the main tutorial story

## Important Honesty Rules Kept

- sorting is taught as a tutorial/demo path, not as a release-facing workload
  family
- `v0.2` released workload families and `v0.4` nearest-neighbor preview
  workloads remain clearly separated
- rendering demos are framed as RTDL-plus-Python applications, not as proof
  that RTDL is a full rendering engine

## Verification

- docs-only slice
- direct consistency review across the new tutorial ladder and existing
  example/docs entry points
- external Gemini review requested on the exact tutorial surface
- runnable sanity commands from the new tutorial path:
  - `PYTHONPATH=src:. python3 examples/rtdl_hello_world.py`
  - `PYTHONPATH=src:. python3 scripts/rtdl_sorting_demo.py --backend cpu_python_reference 3 1 4 1 5 0 2 5`
  - `PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 2`
  - `PYTHONPATH=src:. python3 examples/rtdl_fixed_radius_neighbors.py --backend cpu_python_reference`
  - `PYTHONPATH=src:. python3 examples/visual_demo/rtdl_lit_ball_demo.py --backend cpu_python_reference --compare-backend none --width 32 --height 16 --triangles 64 --output build/rtdl_lit_ball_demo_test.pgm`
- observed result:
  - all five commands completed successfully
