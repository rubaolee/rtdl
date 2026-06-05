# Goal3467 - Shape-Pair Relation Complexity Probe

## Status

Implemented locally; pod validation pending.

Goal3467 adds a generic CuPy relation-stream complexity classifier. It consumes
the same resident shape-pair relation contract used by the bounds-overlap and
witness continuations:

- relation id and flag columns
- relation ordinals
- generic geometry payload columns

It emits device columns for per-row vertex counts, convexity flags, and a
`general_overlay_required` mask. This is not an exact overlay-area primitive.
It is a routing/readiness primitive that tells the exact overlay lane whether a
simple convex clipping continuation is sufficient or whether the general
simple-polygon overlay path is required.

## Why This Goal Exists

The public-CDB RayJoin geometry is not a convex-clip-only workload. A pod
geometry audit found that `br_county.cdb` contains many nonconvex shapes and
hundreds of vertices in the largest rings. Goal3467 turns that observation into
machine-readable active-row evidence over the real relation stream.

## Boundary

This goal does not authorize:

- v2.8 release
- public speedup wording
- broad RT-core speedup wording
- true-zero-copy wording
- RayJoin paper reproduction claims
- RTDL-beats-RayJoin claims
- full exact overlay-area completion claims

The classifier is generic and app-agnostic, but exact overlay-area continuation
for non-integer, non-orthogonal, nonconvex polygons remains open.

## Validation

Local validation:

- `py -3 -m py_compile src\rtdsl\geometry_relation_continuations.py scripts\goal3467_shape_pair_relation_complexity_probe.py`
- `py -3 -m unittest tests.goal3467_shape_pair_relation_complexity_probe_test`

Pod validation target:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python -u scripts/goal3467_shape_pair_relation_complexity_probe.py \
  --iterations 4 \
  --max-rows 65536 \
  --simple-vertex-threshold 64 \
  --output docs/reports/goal3467_shape_pair_relation_complexity_probe_pod_2026-06-05.json
```

## Remaining Work

If the active relation rows require the general overlay path, the next primitive
must be a generic simple-polygon overlay-area continuation. A convex-only
Sutherland-Hodgman-style continuation would be insufficient for the public-CDB
RayJoin benchmark unless it is explicitly routed only to convex rows.
