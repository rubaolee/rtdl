# RTDL Programming Guide

This guide explains how to write RTDL kernels correctly for the current language
surface.

## 1. Start With The Kernel Header

Every RTDL kernel starts with:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
```

Do not vary these values in the current implementation.

Also:

- the kernel function takes no Python arguments
- the body should only use RTDL operations

## 2. Declare Inputs First

Inputs come first and should be given clear domain names:

```python
roads = rt.input("roads", rt.Segments, role="probe")
boundaries = rt.input("boundaries", rt.Segments, role="build")
```

Recommendations:

- use explicit roles
- keep the Python variable name aligned with the input name string
- use built-in geometry types unless a custom layout is necessary

## 3. Add Traversal

Current RTDL only supports BVH traversal:

```python
candidates = rt.traverse(roads, boundaries, accel="bvh")
```

## 4. Add Refinement

Choose one supported predicate.

### For LSI

```python
hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
```

### For PIP

```python
hits = rt.refine(
    candidates,
    predicate=rt.point_in_polygon(exact=False, boundary_mode="inclusive"),
)
```

### For Overlay

```python
seeds = rt.refine(candidates, predicate=rt.overlay_compose())
```

### For Ray/Triangle Hit Count

```python
hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
```

### For Segment/Polygon Hit Count

```python
hits = rt.refine(candidates, predicate=rt.segment_polygon_hitcount(exact=False))
```

### For Point/Nearest Segment

```python
nearest = rt.refine(candidates, predicate=rt.point_nearest_segment(exact=False))
```

## 5. Return Emit

The kernel must end with `return rt.emit(...)`.

```python
return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])
```

## What RTDL Is Not

RTDL is not currently an imperative per-element kernel language.

Do not write:

- `for` loops over inputs
- mutable local accumulators as part of the DSL
- typed kernel arguments like `ray: rt.Ray2D`
- user-written calls like `rt.intersect(...)`
- output objects like `rt.Output[...]`

## Choosing Layouts

Use the default layouts unless you need to be explicit in docs or tests.

Built-in defaults:

- `rt.Segment2DLayout`
- `rt.Point2DLayout`
- `rt.Polygon2DLayout`
- `rt.Triangle2DLayout`
- `rt.Ray2DLayout`

If you write a custom layout, it must still include the required fields for the
chosen geometry type.

## Choosing Roles

Prefer explicit roles.

Good:

```python
points = rt.input("points", rt.Points, role="probe")
polygons = rt.input("polygons", rt.Polygons, role="build")
```

Avoid relying on implicit role assignment unless you are intentionally using the
default behavior.

## Workload Recipes

### Segment Intersection

Use when both inputs are segment sets and you want intersection pairs plus the
intersection point.

### Point In Polygon

Use when probe data are points and build data are polygon references.

### Overlay

Use when both inputs are polygon references and you want overlay seed records
instead of final overlay polygons.

### Ray/Triangle Hit Count

Use when probe data are finite 2D rays and build data are triangles, and you
want one count record per ray.

Recommended ray layout:

- origin: `ox`, `oy`
- direction: `dx`, `dy`
- finite extent: `tmax`
- identifier: `id`

Typical use:

- many random triangles in 2D
- many rays from a center point with random angle and random length
- one emitted result per ray with total hit count

### Segment/Polygon Hit Count

Use when probe data are segments and build data are polygons, and you want one
hit-count record per segment.

### Point/Nearest Segment

Use when probe data are points and build data are segments, and you want one
nearest-segment record per point.

## Current Limitations

- only the current RTDL lowering surface (`backend="rtdl"`, with legacy `rayjoin` compatibility)
- only `float_approx` precision
- only `bvh`
- only six built-in workload predicates
- ray/triangle hit count remains 2D-only
- overlay is a composition-level skeleton, not a finished geometric overlay runtime
- generated OptiX/CUDA output is still backend skeleton code

## Dataset Guidance

For RayJoin-style data:

- load CDB chain files with `rt.load_cdb(...)`
- derive segments with `rt.chains_to_segments(...)`
- derive probe points with `rt.chains_to_probe_points(...)`
- derive polygon refs with `rt.chains_to_polygon_refs(...)`

For synthetic ray-query examples:

- use `examples/rtdl_ray_tri_hitcount.py`
- generate triangles with `make_random_triangles(...)`
- generate rays with `make_center_rays(...)`

## Validation Workflow

To validate a kernel:

1. compile it with `rt.compile_kernel(...)`
2. lower it with `rt.lower_to_execution_plan(...)`
3. generate backend artifacts with `rt.generate_optix_project(...)`

To execute a currently supported kernel locally on CPU:

1. write the RTDL kernel as usual
2. prepare Python-side input records
3. call `rt.run_cpu(kernel_fn, **inputs)`

Example:

```python
rows = rt.run_cpu(
    central_ray_triangle_stats,
    rays=(
        {"id": 1, "ox": 0.0, "oy": 0.0, "dx": 1.0, "dy": 0.0, "tmax": 10.0},
    ),
    triangles=(
        {"id": 10, "x0": 2.0, "y0": -1.0, "x1": 3.0, "y1": 1.0, "x2": 4.0, "y2": -1.0},
    ),
)
```

The CPU simulator:

- compiles the kernel
- validates required input names
- converts records into RTDL reference dataclasses
- dispatches to the workload-specific CPU semantics
- returns rows shaped exactly like the kernel's `emit` fields

### CPU Simulator Input Rules

- segments, points, triangles, and rays may be provided as RTDL reference dataclasses or dictionaries
- dictionaries may contain extra bookkeeping fields; required geometry fields are read and extras are ignored
- polygons are special in simulator mode: provide logical polygon records with `id` and inline `vertices`
- simulator mode currently supports only `precision="float_approx"`

### Embree Execution Mode

RTDL also supports a native local execution path:

```python
rows = rt.run_embree(
    central_ray_triangle_stats,
    rays=(
        {"id": 1, "ox": 0.0, "oy": 0.0, "dx": 1.0, "dy": 0.0, "tmax": 10.0},
    ),
    triangles=(
        {"id": 10, "x0": 2.0, "y0": -1.0, "x1": 3.0, "y1": 1.0, "x2": 4.0, "y2": -1.0},
    ),
)
```

Requirements:

- install Embree locally with `brew install embree`
- current implementation expects Homebrew Embree under `/opt/homebrew/opt/embree`
- current implementation supports the same six workloads as `rt.run_cpu(...)`
- on non-default setups, set `RTDL_EMBREE_PREFIX` and optionally `RTDL_TBB_PREFIX`

Notes:

- `run_embree(...)` uses Embree for traversal/candidate execution on this Mac
- `run_cpu(...)` remains the correctness baseline
- polygons still use logical inline `vertices` inputs in local execution mode
- the current Embree path is a local runtime backend, not a replacement for the future GPU backend

For repository-level validation:

- run `make test`
- run `make run-rtdsl-py`

## Embree Baseline Runners

The project now keeps a frozen baseline integration layer for the current four
workloads.

Run one workload directly:

```sh
PYTHONPATH=src:. python3 -m rtdsl.baseline_runner lsi --backend both
PYTHONPATH=src:. python3 -m rtdsl.baseline_runner pip --backend both
PYTHONPATH=src:. python3 -m rtdsl.baseline_runner overlay --backend both
PYTHONPATH=src:. python3 -m rtdsl.baseline_runner ray_tri_hitcount --backend both
```

This runner:

- chooses a representative dataset if one is not specified
- executes `run_cpu(...)` and/or `run_embree(...)`
- compares results through the frozen baseline comparison policy

The source-of-truth contracts for these runs live in:

- `src/rtdsl/baseline_contracts.py`
- `docs/embree_baseline_contracts.md`

## Embree Baseline Benchmark

Use the local benchmark harness to record warmup-aware timing data:

```sh
PYTHONPATH=src:. python3 -m rtdsl.baseline_benchmark --iterations 3 --warmup 1
PYTHONPATH=src:. python3 -m rtdsl.baseline_summary build/embree_baseline_benchmark.json
```

The benchmark JSON is a local-only artifact written under `build/` and is meant
for the pre-GPU Embree phase. It records:

- backend
- workload
- representative dataset
- warmup count
- iteration timings
- summary timing statistics

## Authoring Checklist

- kernel uses `backend="rtdl"` and `precision="float_approx"`
- every input has a unique name
- `accel="bvh"`
- predicate matches the geometry pair
- emit fields match the workload
- kernel returns `rt.emit(...)`
