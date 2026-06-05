# Goal3471 - Convex Overlay-Area Fast-Path Probe

## Status

Implemented locally; pod validation pending.

Goal3471 adds a generic CuPy convex overlay-area continuation over the existing
shape-pair relation stream. It is exact only for supported convex rows and
returns fail-closed status codes for nonconvex, degenerate, or vertex-budget
rows.

This is the routed fast path described by Goal3470. It does not close the
public-CDB RayJoin exact-overlay gap because Goal3467 showed that most active
rows require general simple-polygon overlay.

## Status Codes

| Code | Meaning |
| --- | --- |
| `0` | convex overlay area computed |
| `1` | unsupported nonconvex row |
| `2` | unsupported vertex budget |
| `3` | unsupported degenerate shape |

## Boundary

This goal does not authorize release, public speedup wording, broad RT-core
speedup wording, true-zero-copy wording, RayJoin paper reproduction claims,
RTDL-beats-RayJoin claims, or full exact overlay-area completion claims.

## Validation

Local validation:

- `py -3 -m py_compile src\rtdsl\geometry_relation_continuations.py scripts\goal3471_convex_overlay_area_fast_path_probe.py`
- `py -3 -m unittest tests.goal3471_convex_overlay_area_fast_path_probe_test`

Pod validation target:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python -u scripts/goal3471_convex_overlay_area_fast_path_probe.py \
  --iterations 4 \
  --max-rows 65536 \
  --simple-vertex-threshold 64 \
  --max-vertices-per-shape 128 \
  --output docs/reports/goal3471_convex_overlay_area_fast_path_probe_pod_2026-06-05.json
```

## Remaining Work

The main RayJoin exact-overlay path still needs a generic simple-polygon
overlay-area continuation for nonconvex/high-vertex rows.

