# Goal1969 CuPy Extent Polygon Candidate Backend

Date: 2026-05-14

Status: implementation slice with pod timing

## Why This Goal Exists

Goal1968 showed that the polygon control rows are no longer primarily limited
by CuPy continuation math. On the RTX 2000 Ada pod, Embree candidate discovery
took about `0.67s` to `0.86s`, while payload construction was about `0.02s`.
With `cpu_all_pairs`, candidate construction became catastrophic.

The design problem is therefore a missing reusable candidate-table handoff: the
app should not have to materialize a huge pair set or pay three row-producing
native calls before the partner continuation can run.

## Implemented Slice

`examples/rtdl_control_apps_cupy_rawkernel.py` now accepts:

```text
--candidate-backend cupy_extent
```

For the authored axis-aligned polygon control rows, this backend computes
overlapping 2D extent candidates with CuPy tensor operations, then feeds the
existing compact `PartnerPairPayloadTable` and RawKernel continuation.

## Boundary

This does not add app semantics to the native engine. It is a partner-side
candidate-table construction path for bounded 2D extents. It does not replace
the future OptiX RT-core candidate path, and it does not prove arbitrary polygon
overlay acceleration.

## Pod Test

The pod run compared `cupy_extent` against v1.8 Python+RTDL for:

| App | Candidate backend | Copies | v1.8 median s | v2 median s | v2/v1.8 | Correct |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `polygon_pair_overlap_area_rows` | `cupy_extent` | 2048 | 0.279780 | 0.081689 | 0.292x | yes |
| `polygon_set_jaccard` | `cupy_extent` | 2048 | 0.233212 | 0.065533 | 0.281x | yes |

This reverses the Goal1968 polygon result: the same rows were `2.764x` to
`3.484x` slower with Embree candidate discovery and more than `100x` slower with
`cpu_all_pairs`. The useful lesson is that a compact partner candidate-table
handoff matters more here than the exact CPU/GPU continuation math.

This is still not an OptiX RT-core result because the pod lacks the OptiX SDK.
v2.0 release claims still require external review and the broader release gates.

Artifact:

- `docs/reports/goal1969_pod_cupy_extent_polygon_control_perf.json`
