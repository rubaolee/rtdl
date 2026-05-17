# Goal2258: Prepared Closed-Shape Membership Count Mode

Status: implementation pending pod timing.

## Purpose

Goal2258 adds a generic count-only surface for prepared OptiX closed-shape
membership:

```text
rtdl_optix_count_prepared_point_closed_shape_membership_2d
PreparedOptixPointClosedShapeMembership2D.count(...)
```

The purpose is to support count-style learner workloads without forcing Python
to materialize every positive membership row as dictionaries. This fits the
stable RTDL primitive direction of generic integer count reductions.

## Boundary

This is not a RayJoin-specific primitive. The ABI uses point, closed shape,
membership, prepared scene, and count vocabulary. RayJoin/PIP names remain in
application harnesses and reports only.

The first implementation intentionally preserves the existing exactness path by
reusing the prepared positive-hit execution and returning its exact row count
after native refinement. It removes Python row materialization, but it is not yet
a pure device-resident output-stream implementation.

## Expected Measurement

Pod timing should compare:

- prepared membership row return,
- prepared membership count return,
- and the existing RayJoin same-query CPU parity count.

No speedup claim is authorized until a pushed-commit pod artifact and external
review exist.
