# RTDL Quick Tutorial

This is the shortest path to writing and running a small RTDL program.

If you are evaluating RTDL for the first time, the key idea is:

- RTDL is the geometric-query core
- Python is the surrounding application language

So the normal first step is not a giant benchmark. It is a tiny runnable
program that shows the RTDL execution shape clearly.

Environment assumptions for this tutorial:

- clone the repo as `rtdl`
- run commands from the repo root
- use Python `3.10+`
- keep the `PYTHONPATH=src:.` prefix so Python imports the local `rtdsl`
  package from `src/rtdsl/`

If you want the recommended optional package for the demo/application path:

```bash
python3 -m pip install -r requirements.txt
```

## Fastest First Run

From the repository root:

```bash
PYTHONPATH=src:. python3 examples/rtdl_hello_world.py
```

The `PYTHONPATH=src:.` prefix tells Python to import the local RTDL package
from this checkout.

Expected output:

```text
hello, world
```

If that works, your next two useful commands are:

```bash
PYTHONPATH=src:. python3 examples/rtdl_hello_world_backends.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
```

If you want to jump directly into the active `v0.4` line, the two cleanest
nearest-neighbor examples are:

```bash
PYTHONPATH=src:. python3 examples/rtdl_fixed_radius_neighbors.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_knn_rows.py --backend cpu_python_reference
```

If you want application-shaped nearest-neighbor examples instead of bare
workload kernels, start with:

```bash
PYTHONPATH=src:. python3 examples/rtdl_service_coverage_gaps.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_event_hotspot_screening.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_facility_knn_assignment.py --backend cpu_python_reference
```

Those three commands teach three different things:

- `rtdl_hello_world.py`: the smallest possible RTDL execution shape
- `rtdl_hello_world_backends.py`: how backend selection changes the same scene
- `rtdl_segment_polygon_hitcount.py`: what a release-facing workload example looks like

The two nearest-neighbor commands show what the active `v0.4` workload family
looks like in public user-facing form.

## What RTDL programs do

An RTDL program usually has the same shape:

1. declare the input geometry sets
2. traverse one set against another with an acceleration structure
3. refine the candidate pairs with a predicate
4. emit rows

In code, that usually looks like this:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def my_kernel():
    probe = rt.input("probe", ..., role="probe")
    build = rt.input("build", ..., role="build")
    candidates = rt.traverse(probe, build, accel="bvh")
    refined = rt.refine(candidates, predicate=...)
    return rt.emit(refined, fields=[...])
```

## Hello, world

The smallest RTDL example in this repo is:

- `examples/rtdl_hello_world.py`

It is a tiny ray-query program, not a spatial join. One horizontal ray is shot
through a scene with three labeled rectangles:

- one rectangle is above the ray and should be missed
- one rectangle is on the ray path and should be hit
- one rectangle is above the ray and should be missed

The hit rectangle is represented by two triangles, because the current RTDL ray
example path uses rays against triangles.

So the RTDL kernel reports a primitive `hit_count` of `2`, not `1`. The final
program output reconstructs the visible hit rectangle from the scene record and
prints that rectangle's label.

Each visible rectangle has its own ID and label in the scene definition. If the
middle rectangle is hit, the program prints that rectangle's label:

- `hello, world`

## Why this is a good first example

This example shows the RTDL execution pattern without the heavier parts of the
RayJoin workload family:

- no dataset ingestion
- no PostGIS
- no command-line parsing
- just one ray, a few triangles, one RTDL call, and one printed result

## Run it

From the repository root:

```bash
PYTHONPATH=src:. python3 examples/rtdl_hello_world.py
```

Expected output:

```text
hello, world
```

Internally, the ray hits exactly one visible rectangle and misses the other
two. The RTDL kernel still reports a triangle hit count of `2`, because the
visible hit rectangle is encoded as two triangles. The final printed string is
therefore connected to the hit rectangle's scene record rather than being a
separate hardcoded output.

## Try another backend

The example is intentionally minimal and uses only:

- `rt.run_cpu_python_reference(...)`

That keeps the first program short and easy to read. After that, you can look
at the larger examples for other backends (Embree, OptiX, and Vulkan are
supported for most workloads).

If you want the same scene with backend switching, use:

- `examples/rtdl_hello_world_backends.py`

Example:

```bash
PYTHONPATH=src:. python3 examples/rtdl_hello_world_backends.py --backend cpu_python_reference
```

The released workload examples use the same general pattern, just with more
realistic inputs and emitted rows.

## Next steps

After this hello-world example, the best next files are:

- `docs/release_facing_examples.md`
- `examples/rtdl_fixed_radius_neighbors.py`
- `examples/rtdl_knn_rows.py`
- `examples/rtdl_service_coverage_gaps.py`
- `examples/rtdl_event_hotspot_screening.py`
- `examples/rtdl_facility_knn_assignment.py`
- `examples/rtdl_segment_polygon_hitcount.py`
- `examples/rtdl_segment_polygon_anyhit_rows.py`
- `examples/rtdl_polygon_set_jaccard.py`
- `examples/visual_demo/rtdl_lit_ball_demo.py`
- `docs/features/README.md`
- `docs/architecture_api_performance_overview.md`

If you want a clear map of which example directories are public versus
historical, also read:

- `examples/README.md`

That path moves from a tiny ray-query example to the current release-facing
spatial workloads and then to the broader architecture/performance story.

If you already know which workload family you want, jump straight to:

- [Release-Facing Examples](release_facing_examples.md)
- [Feature Homes](features/README.md)

## RTDL Plus Python

RTDL is not only a fixed menu of named workloads. The current public surface is
still bounded, but users can already combine RTDL kernels with Python
application logic.

That is often the most practical way to use the system:

- RTDL handles the geometric query core
- Python handles grouping, summaries, reporting, or visual output

The clearest small example is:

- [rtdl_lit_ball_demo.py](../examples/visual_demo/rtdl_lit_ball_demo.py)

That demo uses RTDL only for ray/triangle hit relationships, then uses Python
to reconstruct the visible span, compute brightness, print ASCII, and write a
real `.pgm` image. It is not a claim that RTDL v0.2.0 is a full rendering
system. It is a concrete example of RTDL working well as the geometric core of
a Python application.

## If You Only Remember Three Things

- use RTDL when the hard part of your problem is geometric querying
- start with `examples/rtdl_hello_world.py`, then a release-facing example
- treat RTDL as the core query engine and Python as the application layer
