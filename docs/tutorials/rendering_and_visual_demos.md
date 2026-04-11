# Tutorial: RTDL Plus Python Rendering

This tutorial is for readers who want to understand the 2D/3D demo side of the
repo without misunderstanding RTDL as a full rendering engine.

The correct model is:

- RTDL handles the geometric-query core
- Python handles the surrounding scene/app/output logic

## What You Will Learn

- how RTDL participates in the visual demos
- why the visual demos belong in the repo
- where to start if you want a small rendering-oriented example

## First Demo To Read

Start with:

- [examples/visual_demo/rtdl_lit_ball_demo.py](../../examples/visual_demo/rtdl_lit_ball_demo.py)

Run:

```bash
PYTHONPATH=src:. python3 examples/visual_demo/rtdl_lit_ball_demo.py --backend cpu_python_reference --compare-backend none --width 240 --height 240 --triangles 512 --output build/rtdl_lit_ball_demo_hq.pgm
```

This is the best small demonstration of the RTDL-plus-Python split:

- RTDL answers ray/triangle hit-count questions
- Python reconstructs visible spans, computes brightness, and writes the image

## Then Move To The Main 3D Demo

Primary source:

- [examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py](../../examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py)

Small sanity check:

```bash
PYTHONPATH=src:. python3 examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py --backend cpu_python_reference --compare-backend none --width 48 --height 48 --latitude-bands 6 --longitude-bands 12 --frames 1 --jobs 1 --shadow-mode rtdl_light_to_surface --output-dir build/quick_hidden_star_demo
```

This example is larger, but it teaches the same boundary:

- RTDL owns primary visibility and shadow-query work
- Python owns animation, shading, frame management, and output packaging

## Why This Tutorial Exists

Beginners often see the visual demos and ask one of two wrong questions:

1. “Is RTDL secretly just a renderer?”
2. “Are these demos unrelated to the language?”

The honest answer is:

- RTDL is not a full rendering engine
- the demos still matter because they show RTDL acting as a real geometric core
  inside larger Python applications

## Next Pages

For the workload side of RTDL, return to:

- [Segment And Polygon Workloads](segment_polygon_workloads.md)
- [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)

For broader example indexing:

- [Release-Facing Examples](../release_facing_examples.md)
- [examples/README.md](../../examples/README.md)
