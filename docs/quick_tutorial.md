# RTDL Quick Tutorial

This page is the fastest way for a beginner to get a first successful RTDL run
and then move into the right tutorial track.

If you only want one mental model, use this:

- RTDL is the geometric-query core
- Python is the surrounding application language

## Fastest First Run

From the repository root:

```bash
PYTHONPATH=src:. python3 examples/rtdl_hello_world.py
```

Expected output:

```text
hello, world
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_hello_world.py
```

## Fastest Second Run

If the first run worked, try one of these next:

```bash
PYTHONPATH=src:. python3 examples/rtdl_hello_world_backends.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
PYTHONPATH=src:. python3 examples/rtdl_fixed_radius_neighbors.py --backend cpu_python_reference
```

These show three different entry points:

- same tiny program across backends
- released workload-family example
- active nearest-neighbor preview example

## The Tutorial Ladder

After the first successful run, follow this learning order:

1. [Hello World](tutorials/hello_world.md)
2. [Sorting Demo](tutorials/sorting_demo.md)
3. [Segment And Polygon Workloads](tutorials/segment_polygon_workloads.md)
4. [Nearest-Neighbor Workloads](tutorials/nearest_neighbor_workloads.md)
5. [RTDL Plus Python Rendering](tutorials/rendering_and_visual_demos.md)

Or use the full tutorial hub:

- [RTDL Tutorials](tutorials/README.md)

## Which Tutorial Should You Read?

Read:

- [Hello World](tutorials/hello_world.md)
  - if you want the smallest possible RTDL example
- [Sorting Demo](tutorials/sorting_demo.md)
  - if you want to see RTDL inside a compact Python demo
- [Segment And Polygon Workloads](tutorials/segment_polygon_workloads.md)
  - if you want the stable released workload families
- [Nearest-Neighbor Workloads](tutorials/nearest_neighbor_workloads.md)
  - if you want the active `v0.4` preview line
- [RTDL Plus Python Rendering](tutorials/rendering_and_visual_demos.md)
  - if you want the 2D/3D demo/application side

## If You Only Remember Three Things

- start with `examples/rtdl_hello_world.py`
- learn RTDL through the tutorial ladder, not by jumping straight into archive reports
- treat RTDL as the core query engine and Python as the application layer
