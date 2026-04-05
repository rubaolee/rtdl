# RTDL Quick Tutorial

This is the shortest path to writing and running a small RTDL program.

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
at the larger examples for other backends.

If you want the same scene with backend switching, use:

- `examples/rtdl_hello_world_backends.py`

Example:

```bash
PYTHONPATH=src:. python3 examples/rtdl_hello_world_backends.py --backend cpu_python_reference
```

## Next steps

After this hello-world example, the best next files are:

- `examples/rtdl_language_reference.py`
- `examples/rtdl_sorting_single_file.py`
- `docs/architecture_api_performance_overview.md`

The sorting example is especially useful because it is a task readers
already understand. It shows that RTDL is not only for spatial joins: you can
express an unusual computation in RTDL, run it across backends, and then verify
the result against ordinary Python sorting.

That path moves from a tiny ray-query example, to a familiar sorting task
written in RTDL, and then to the broader architecture/performance story.
