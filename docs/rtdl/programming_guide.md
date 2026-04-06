# RTDL Programming Guide

This guide explains **how to author RTDL kernels correctly**.

Scope of this file:

- kernel shape
- how to choose inputs, roles, and predicates
- how to execute kernels through the current runtime surface
- how to validate new kernels

This guide is intentionally different from:

- [DSL Reference](dsl_reference.md): exact contract
- [Workload Cookbook](workload_cookbook.md): copyable examples

## 1. Start With The Current Kernel Header

Current canonical header:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
```

Current rules:

- use `backend="rtdl"` as the canonical spelling
- `backend="rayjoin"` remains compatibility-only
- current lowering accepts only `precision="float_approx"`
- kernel functions take no Python arguments

## 2. Declare Inputs Clearly

Declare inputs first and use meaningful domain names:

```python
roads = rt.input("roads", rt.Segments, role="probe")
boundaries = rt.input("boundaries", rt.Segments, role="build")
```

Recommendations:

- prefer explicit `role=...`
- keep the variable name aligned with the input name
- use built-in layouts unless you have a concrete reason not to

## 3. Use The Standard Kernel Shape

Most current RTDL kernels follow this pattern:

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def some_query():
    left = rt.input("left", rt.Segments, role="probe")
    right = rt.input("right", rt.Segments, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(
        hits,
        fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
    )
```

Semantics:

1. `rt.input(...)` declares geometry and roles
2. `rt.traverse(...)` defines candidate generation
3. `rt.refine(...)` applies the geometric predicate
4. `rt.emit(...)` defines the output row schema

## 4. Choose The Right Predicate

Current built-in predicate families:

- `rt.segment_intersection(exact=False)`
- `rt.point_in_polygon(exact=False, boundary_mode="inclusive")`
- `rt.overlay_compose()`
- `rt.ray_triangle_hit_count(exact=False)`
- `rt.segment_polygon_hitcount(exact=False)`
- `rt.segment_polygon_anyhit_rows(exact=False)`
- `rt.point_nearest_segment(exact=False)`

Important boundaries:

- `boundary_mode="inclusive"` is the only accepted PIP boundary mode
- current paths are approximate/float-based, not exact arithmetic
- overlay emits overlay seeds, not final polygon fragments

## 5. Choose The Right Execution Path

### Oracle

Use `rt.run_cpu(...)` when:

- correctness is the priority
- you are validating a new kernel
- you need the project ground truth

The old Python reference path is still available as:

- `rt.run_cpu_python_reference(...)`

### Embree

Use `rt.run_embree(...)` when:

- you want the controlled CPU backend
- you need real backend timing or behavior

Execution modes:

- `dict`: easiest, slowest
- `raw`: lower-overhead native row view
- prepared raw: best repeated-execution path

### OptiX

Use `rt.run_optix(...)` when:

- you are on a supported NVIDIA host
- you want the controlled GPU backend

Current trusted GPU path:

- bounded, correctness-checked runs
- trusted PTX generation on `192.168.1.20` uses the `nvcc` fallback

### Vulkan

Use `rt.run_vulkan(...)` only when:

- you are explicitly working on the current bounded Vulkan path
- you understand that Vulkan is correctness-closed only on the accepted bounded
  Linux surface and is still provisional beyond that

Current boundary:

- Vulkan remains in-repo and usable for directed work
- it is now parity-clean on the accepted bounded Linux surface
- it is still not validated to the same larger-scale acceptance level as Embree
  or the accepted OptiX path

## 6. Validation Workflow

When adding or changing a kernel:

1. compile it
2. lower it
3. inspect the plan if needed
4. run it through the oracle
5. compare it against Embree and/or OptiX when relevant
6. compare accepted bounded real-data packages against indexed PostGIS ground truth when the goal requires an external checker

Typical flow:

```python
compiled = rt.compile_kernel(kernel_fn)
plan = rt.lower_to_execution_plan(compiled)
rows = rt.run_cpu(kernel_fn, **inputs)
```

For backend validation:

```python
oracle_rows = rt.run_cpu(kernel_fn, **inputs)
embree_rows = rt.run_embree(kernel_fn, **inputs)
```

or

```python
oracle_rows = rt.run_cpu(kernel_fn, **inputs)
optix_rows = rt.run_optix(kernel_fn, **inputs)
```

## 7. Current Authoring Boundaries

RTDL is not currently:

- an imperative per-element kernel language
- a general scheduling language
- an exact computational-geometry system
- a fully general backend-independent optimizer

Avoid:

- explicit loops in the DSL body
- custom mutable accumulation patterns
- unsupported precision modes
- unsupported geometry/predicate combinations

## 8. Where To Go Next

- for exact contracts: [DSL Reference](dsl_reference.md)
- for workload snippets: [Workload Cookbook](workload_cookbook.md)
- for project-level context: [Feature Guide](../rtdl_feature_guide.md)
