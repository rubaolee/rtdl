# Kernel Shape And Backends

Status: current v2.10 source-tree tutorial.

Goal: understand what an RTDL primitive does before choosing partners or
benchmark apps.

## The Shape

Most RTDL examples follow this pattern:

```text
input -> traverse -> refine -> emit
```

| Stage | Meaning |
| --- | --- |
| `input` | Python prepares typed columns, points, boxes, rays, segments, or payloads. |
| `traverse` | RTDL asks a backend to search candidate geometry or relationships. |
| `refine` | The primitive applies the generic predicate or score rule. |
| `emit` | The primitive returns flags, counts, rows, witnesses, or summaries. |

The names stay generic. A benchmark app can call the result "DBSCAN", "RayJoin",
or "Hausdorff" in Python, but the engine should expose contracts such as
fixed-radius counts, point-nearest summaries, grouped reductions, or segment
intersection rows.

## Backend Choice

| Backend | Use it for | Notes |
| --- | --- | --- |
| CPU reference | First correctness run and debugging | Always the safest learner route. |
| Embree | CPU ray-tracing backend work | Useful on ordinary CPU machines. |
| OptiX | NVIDIA GPU RT-core routes | Requires a built `librtdl_optix.so` and CUDA-capable hardware. |

RTDL does not hide backend choice. A tutorial should make the chosen backend
visible in the command, result metadata, or code.

## OptiX Setup Boundary

Only run OptiX examples after the native library is built and exported:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
```

If that variable is missing, stay on CPU or Embree tutorials. Missing OptiX
setup is an environment limitation, not a Python language failure.

## What Not To Do

Do not start by inventing an app-specific engine call. Search for a generic
primitive first. If the primitive returns a typed stream or summary that your
app can continue, keep the app-specific meaning in Python.

## Next

Continue with [Primitive Discovery](03_primitives_and_discovery.md).
