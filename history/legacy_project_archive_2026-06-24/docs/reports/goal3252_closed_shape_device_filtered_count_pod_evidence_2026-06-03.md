# Goal3252: Closed-Shape Device-Filtered Count Pod Evidence

Date: 2026-06-03

## Purpose

Goal3251 added an explicit fast scalar count path for prepared generic
point/closed-shape membership:

```text
rtdl_optix_count_prepared_point_closed_shape_membership_device_filtered_2d
```

The new path is deliberately separate from the exact `.count(...)` API. It uses
the device-side closed-shape membership predicate, returns only a scalar count,
and avoids candidate-row materialization, candidate download, and host exact
refinement. The exact host-refined count remains the correctness authority.

Goal3252 measures the new path on the current RayJoin PIP same-slice row.

## Artifacts

- Runner:
  `scripts/goal3252_closed_shape_device_filtered_count_probe.py`
- Pod JSON:
  `docs/reports/goal3252_closed_shape_device_filtered_count_probe_pod_2026-06-03.json`
- Pod stdout:
  `docs/reports/goal3252_closed_shape_device_filtered_count_probe_pod_2026-06-03.stdout`

The clean pod run used commit `1b12cb1660f2bcb42c8416d585c95a35291145c1` and
reported `source_dirty: []`.

## Result

Dataset:

```text
/root/rtdl_goal3151/data/rayjoin_public_cdb/br_county_start0_count512.cdb
```

Environment:

```text
RTDL_OPTIX_POINT_PRIMITIVE_QUERY_HALF_EXTENT=0.25
```

| Route | Median query | Counts | Status |
| --- | ---: | ---: | --- |
| Exact prepared closed-shape count | `0.895219 ms` | `1430 x 9` | exact authority |
| Device-filtered prepared closed-shape count | `0.785675 ms` | `1430 x 9` | matches exact on this slice |

The device-filtered path is `1.14x` faster than the exact count path on this
slice. Phase telemetry shows the intended behavior:

- `mode`: `device_filtered_count`
- candidate count traversal: about `0.725 ms`
- candidate write: `0`
- candidate download: `0`
- exact refine: `0`
- raw/emitted count: `1430`

## Interpretation

Goal3252 is a useful primitive/runtime improvement, but it is not enough to
close the RayJoin PIP gap. Compared with Goal3248's RayJoin PIP median
(`0.193803 ms`), the new RTDL device-filtered count is still about `4.05x` slower on the same bounded query/count comparison.

The important lesson is diagnostic: once row materialization and host exact
refinement are removed, the remaining cost is still mostly the generic
closed-shape traversal/predicate itself. The next real RayJoin PIP optimization
needs a stronger generic membership/count design, not more host-side cleanup.
Candidates include a tighter closed-shape membership primitive, better shape
indexing/probe policy, or a generic device-resident grouped continuation that
does less work per query while preserving app-agnostic engine boundaries.

## Boundary

Goal3252 does not authorize release, public speedup claims, broad RT-core
speedup claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.

The narrow accepted conclusion is: on this measured RayJoin PIP same-slice row,
the new generic device-filtered scalar count matches the exact count and removes
row/download/refine overhead, but the remaining traversal cost still leaves
RayJoin faster.
