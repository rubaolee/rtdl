# Goal2262: Exact Prepared Closed-Shape Count Without Final Rows

Status: implementation pending pod timing.

## Purpose

Goal2258 added a generic prepared closed-shape `count(...)` API, but the first
native implementation still called the row-return path and freed the final
membership rows. Goal2262 makes the count implementation more direct:

- run the same prepared OptiX candidate path,
- download compact candidate rows for exact refinement,
- count exact hits natively,
- and return only the scalar count to Python.

This avoids allocating the final `RtdlPointClosedShapeMembershipRow` array in
the native count path.

## Boundary

The implementation remains exact because it keeps the host GEOS/inclusive
refinement step used by row-return membership. It is therefore not a pure
device-resident stream yet. The ABI remains app-agnostic: point, closed shape,
membership, prepared scene, and count.

## Expected Measurement

Pod timing should compare Goal2259's first count mode to this direct native
count. No speedup claim is authorized until pushed-commit pod evidence and
external review exist.
