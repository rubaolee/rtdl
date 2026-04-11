# Tutorial: Hello World

This is the best first RTDL program in the repo.

It teaches the smallest important idea:

- RTDL handles the geometric query
- Python handles the surrounding program

## What You Will Learn

- how to run a local RTDL program from the repo
- the basic `input -> traverse -> refine -> emit` kernel shape
- how the same small scene can run on different backends

## First Command

From the repo root:

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

## What The Program Does

The scene has:

- one horizontal ray
- three labeled rectangles
- one visible rectangle on the ray path

The current hello-world path uses rays against triangles, so each rectangle is
represented as two triangles.

That means the RTDL kernel reports a primitive hit count of `2`, while the
surrounding Python program maps that back to the visible rectangle label and
prints:

- `hello, world`

## Kernel Shape

The same structure appears in many RTDL kernels:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def my_kernel():
    probe = rt.input("probe", ..., role="probe")
    build = rt.input("build", ..., role="build")
    candidates = rt.traverse(probe, build, accel="bvh")
    refined = rt.refine(candidates, predicate=...)
    return rt.emit(refined, fields=[...])
```

For this example, the concrete kernel is in:

- [examples/rtdl_hello_world_backends.py](../../examples/rtdl_hello_world_backends.py)

## Try A Different Backend

Run:

```bash
PYTHONPATH=src:. python3 examples/rtdl_hello_world_backends.py --backend cpu_python_reference
```

Then try:

```bash
PYTHONPATH=src:. python3 examples/rtdl_hello_world_backends.py --backend cpu
PYTHONPATH=src:. python3 examples/rtdl_hello_world_backends.py --backend embree
```

If your machine is set up for GPU backends:

```bash
PYTHONPATH=src:. python3 examples/rtdl_hello_world_backends.py --backend optix
PYTHONPATH=src:. python3 examples/rtdl_hello_world_backends.py --backend vulkan
```

## What To Notice

- the scene description stays the same
- the kernel definition stays the same
- only the runner/backend changes

That is the core authoring pattern to remember.

## Next Tutorial

If you want the next smallest programmable example, go to:

- [Sorting Demo](sorting_demo.md)

If you want to jump straight into public workload examples, go to:

- [Segment And Polygon Workloads](segment_polygon_workloads.md)
- [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)
