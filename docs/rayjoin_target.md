# RayJoin Target

## Why RayJoin is the Right First Backend

RayJoin already demonstrates three properties that make it the right first target for RTDL:

- the workload is not graphics, but it maps well to RT-core traversal,
- the implementation depends on OptiX/CUDA details that are too low level for most users, and
- the paper and codebase already expose clear abstractions to lift into a DSL.

## What RTDL Should Abstract

For a RayJoin-style system, users should not need to directly program:

- ray generation versus intersection shader split,
- hit program plumbing,
- payload register packing,
- BVH build invocation details,
- shader binding table setup,
- OptiX module and program group creation,
- launch dimensions, and
- cache invalidation workarounds.

These are backend concerns. They are important for performance, but they should be compiler responsibilities.

## What RTDL Should Keep Visible

The source language should preserve the choices that materially affect correctness or performance:

- query family: `lsi`, `pip`, `touches`, `intersects`, `intersection`,
- geometry roles: build side versus probe side,
- precision mode: fast, conservative, exact,
- output policy: boolean, candidate pairs, exact intersections, overlay fragments,
- optional batching or memory budget hints.

## First Lowering Model

The initial lowering target for RayJoin should produce an explicit backend plan with these stages:

1. Input normalization
   Validate geometry kinds and assign left/right roles.
2. Precision policy selection
   Choose the representation strategy and conservative bounds rules.
3. Acceleration planning
   Decide which side builds the BVH and how queries are batched.
4. Ray formulation
   Convert the high-level query to ray primitives and hit semantics.
5. Result materialization
   Emit candidate pairs, exact intersections, or derived overlay structures.

This plan is a better first milestone than full code generation because it lets the project stabilize semantics before binding tightly to OptiX internals. In this repository, that plan now feeds a skeleton code generator so the lowering boundary is visible and testable.

## Initial Python Surface Syntax

The seed Python-hosted syntax in this repository is intentionally compact:

```python
import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="exact")
def county_zip_join():
    left = rt.input("left", rt.Segments)
    right = rt.input("right", rt.Segments)
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=True))
    return rt.emit(hits, fields=["left_id", "right_id", "intersection_point"])
```

That is enough to validate the core abstraction boundary:

- the user states intent,
- the compiler builds an RT-specific IR and decides the backend plan,
- the backend carries the OptiX/CUDA complexity.
