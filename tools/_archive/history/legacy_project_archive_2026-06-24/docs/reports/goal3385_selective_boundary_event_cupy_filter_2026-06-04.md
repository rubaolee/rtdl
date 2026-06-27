# Goal3385 - Selective Boundary-Event CuPy Filter

Date: 2026-06-04

Verdict: implemented-with-boundary.

## Purpose

Goal3383 rejected simple topology-only ambiguity signals for a default
owner-face route. Boundary-event exploration then showed that strict
zero-distance boundary events are a useful generic signal for selected
candidate rows, but only when the caller or a separately validated signal tells
the pipeline which points should be reconciled.

Goal3385 adds a generic CuPy continuation:

```python
run_selective_closed_shape_boundary_event_membership_pipeline_cupy(...)
```

For caller-selected point ids, it keeps only candidate `(point_id, shape_id)`
pairs that also appear as boundary-event pairs with `crossing_t == 0` by
default. Candidate rows for all non-selected points pass through unchanged.

## Boundary

The helper is generic and app-agnostic:

- it does not know about RayJoin, CDB, GIS, or owner faces;
- it does not infer which points are ambiguous;
- it does not derive ownership or priority;
- it does not authorize a native default route.

It is an explicit continuation primitive that a caller can compose after a
separate, reviewed ambiguity-selection step.

This goal does not authorize release, public speedup, RayJoin reproduction,
RTDL-beats-RayJoin, RT-core speedup, or true-zero-copy claims.

## Verification

The unit test pins:

- selected rows are filtered by zero-boundary event pairs;
- non-selected rows pass through unchanged;
- contract validation exposes the new helper;
- the report keeps the no-default-route boundary.
