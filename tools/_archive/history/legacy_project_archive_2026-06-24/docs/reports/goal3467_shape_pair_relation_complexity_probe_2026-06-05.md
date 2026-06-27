# Goal3467 - Shape-Pair Relation Complexity Probe

## Status

Implemented and validated on the RTX A5000 pod.

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

Pod validation:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python -u scripts/goal3467_shape_pair_relation_complexity_probe.py \
  --iterations 4 \
  --max-rows 65536 \
  --simple-vertex-threshold 64 \
  --output docs/reports/goal3467_shape_pair_relation_complexity_probe_pod_2026-06-05.json
```

- Artifact:
  `docs/reports/goal3467_shape_pair_relation_complexity_probe_pod_2026-06-05.json`
- Stdout:
  `docs/reports/goal3467_shape_pair_relation_complexity_probe_pod_2026-06-05.stdout`
- Commit under test:
  `afbbdb35516c5cfc432a029be19206e6011d3a31`
- GPU:
  NVIDIA RTX A5000, driver 580.126.09
- Dataset:
  `br_county.cdb` (15,700 left shapes) versus
  `br_county_start256_count1024.cdb` (949 right shapes)
- Pod unit test:
  `PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so python -m unittest tests.goal3467_shape_pair_relation_complexity_probe_test`

The packet produced four stable iterations:

| Measure | Value |
| --- | ---: |
| active relation rows | 4,543 |
| both-convex active rows | 168 |
| nonconvex active rows | 4,375 |
| active rows above 64 vertices on at least one side | 1,033 |
| general-overlay-required active rows | 4,375 |
| max left vertices among active rows | 573 |
| max right vertices among active rows | 566 |
| max pair vertices among active rows | 1,132 |
| convex-only clipping sufficient for all rows | false |

Timing summary:

| Phase | Median Seconds | Min Seconds | Max Seconds |
| --- | ---: | ---: | ---: |
| relation columns | 0.004499 | 0.003524 | 0.356541 |
| complexity classification | 0.001161 | 0.000925 | 4.301191 |

The first complexity iteration includes CuPy RawKernel compilation and CUDA
setup. Steady-state classification is small compared with the current witness
continuation packet, but the classification result is more important than the
timing: 4,375 of 4,543 active relation rows require the general simple-polygon
overlay path. A convex-only clipping continuation can be useful as a routed
fast path for the 168 both-convex rows, but it cannot close the RayJoin public
CDB exact-overlay gap by itself.

## Remaining Work

If the active relation rows require the general overlay path, the next primitive
must be a generic simple-polygon overlay-area continuation. A convex-only
Sutherland-Hodgman-style continuation would be insufficient for the public-CDB
RayJoin benchmark unless it is explicitly routed only to convex rows.
