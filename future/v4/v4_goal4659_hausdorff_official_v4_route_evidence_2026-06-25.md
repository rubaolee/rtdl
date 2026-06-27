# V4 Goal4659 Hausdorff Official V4 Route Evidence

Date: 2026-06-25

Status: `goal4659_hausdorff_v4_official_route_correctness_repair_measured_not_release`

## Purpose

Goal4659 tests whether a partial V4 app row, `hausdorff_xhd`, can become a
real app-level V4 route instead of remaining only operator coverage.

This goal implements and measures a generic route:

- producer: `v4_point_group_nearest_witness_2d_device_arrays`
- continuation: `global_argmax_u32_f64_partner_columns(partner="torch")`
- app composition: two directed nearest-witness passes plus one undirected max
- forbidden shortcut avoided: no Hausdorff-specific native kernel

## Code Changes

- `src/rtdsl/partner_adapters.py`
  - Added Torch support to the generic `global_argmax_u32_f64_partner_columns`
    continuation.
  - The Torch path uses int64 masking/reduction internally because CUDA Torch
    does not support `where` on `uint32`.
- `examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
  - Added `partner="torch"` support to `--backend optix_device_max_nearest`.
  - The Torch path uses the official V4 point-group front door:
    `rtdsl.v4_point_group.prepare_point_group_nearest_witness_2d_device_arrays_v4`.
  - Added an optional coordinate-normalized chunk mode for large-coordinate
    exactness. It splits source points by x-span, adds a radius halo on the
    target side, translates each chunk to a local origin, then calls the same
    V4 point-group surface and generic Torch global argmax. This is not a
    Hausdorff-specific native kernel.

## Evidence

Evidence directory:

`future/v4/evidence/v4_goal4659_hausdorff_v4_route_20260625/`

Machine summary:

`future/v4/evidence/v4_goal4659_hausdorff_v4_route_20260625/summary.json`

## Main Results

| Scale | Row | Correct | Primary metric |
| ---: | --- | --- | ---: |
| 65,536 points/side | V2.14 Embree directed summary | true | 68.837892s |
| 65,536 points/side | V3.0.2 CuPy device-max route | true | 0.008707s |
| 65,536 points/side | V4 Torch official route | true | 0.002632s |
| 262,144 points/side | V2.14 Embree directed summary | true | 823.278458s |
| 262,144 points/side | V3.0.2 CuPy device-max route | true | 0.003180s |
| 262,144 points/side | V4 Torch official route | true | 0.002525s |
| 1,048,576 points/side | V3.0.2 CuPy device-max route | false | 0.007817s |
| 1,048,576 points/side | V4 Torch official route | false | 0.007518s |
| 1,048,576 points/side | V4 Torch official route, coordinate-normalized | true | 0.015844s |

Ratios from `summary.json`:

- 65,536 points/side: V4 hot path is `3.309x` faster than V3.0.2 CuPy.
- 262,144 points/side: V4 hot path is `1.260x` faster than V3.0.2 CuPy.
- 262,144 points/side: V4 hot path is `326,053x` faster than V2.14 Embree's
  CPU directed-summary primary metric.
- 1,048,576 points/side: coordinate-normalized V4 passes correctness, but is
  not a speed win. It is `0.493x` of the V3.0.2 CuPy hot metric and `0.475x`
  of the unnormalized V4 hot metric; those two comparison rows fail
  correctness, so this is recorded as a correctness repair, not a speed claim.

## Correctness Boundary

The unnormalized 1,048,576 points/side row fails correctness for both V3.0.2
CuPy and V4 Torch:

- expected exact Hausdorff distance: `0.30000000000000004`
- observed distance: `0.32015618681907654`

This is not a Torch continuation bug. Both V3 and V4 use the same native
point-group nearest-witness producer, whose metadata states:

`float32_computed_float64_output`

The tiled fixture grows absolute x coordinates with the copy index. At the
1,048,576 points/side scale, the coordinate magnitude is large enough that
float32 distance computation loses the small 0.2-0.3 distance precision needed
for exact Hausdorff parity.

The coordinate-normalized V4 mode repairs that exactness boundary at the same
1,048,576 points/side scale:

- normalized observed distance: `0.2999999523162842`
- expected exact Hausdorff distance: `0.30000000000000004`
- coordinate-normalization span: `1000000`
- chunks: `3` directed chunks for A-to-B and `3` directed chunks for B-to-A
- hot metric: `0.015843737870454788s`
- prepare metric: `12.314798556268215s`

This is a correctness repair and a useful V4 route-strengthening result. It is
not a cold-path performance win.

A span sweep was also run at 1M points/side:

- `1000000`: passed correctness
- `1200000`, `1500000`, `1800000`, `2000000`: failed correctness with the same
  `0.32015618681907654` distance as the unnormalized row

So `1000000` is the current measured safe span boundary for this fixture and
route. Compared with the earlier passing `700000` span row, it reduces chunk
count from `4+4` to `3+3`, improves prepare from `14.834420178085566s` to
`12.314798556268215s`, and improves hot from `0.01894262805581093s` to
`0.015843737870454788s`.

## Interpretation

This is real V4 progress:

- a formerly partial app row now has a working official V4 route through a
  measured V4 operator surface;
- the hot path beats the V3.0.2 CuPy route at correctness-passing scales;
- the route remains generic operator composition, not an app-specific kernel.
- the same generic V4 route now has a correctness-passing large-coordinate
  mode at 1M points/side.

It is not enough for final formal high-performance V4:

- the 1M-point exact row only passes with coordinate-normalized chunking;
- the coordinate-normalized 1M hot path is slower than the unnormalized rows,
  although those unnormalized rows are incorrect;
- V4 cold prepare is slower than V3.0.2 on the 262k-point and normalized 1M rows;
- the evidence supports a prepared/reuse hot-path claim, not a single-shot wall
  claim;
- release wording must include the coordinate precision boundary.

## Next Engineering Decision

Continue from Goal4659 only if the next goal directly addresses one of these
release blockers:

1. Reduce V4 prepare overhead so the official route is not only a hot-path win.
2. Decide whether coordinate-normalized chunking becomes a documented route
   option or whether the native point-group producer needs a higher-precision
   distance mode.
3. Add the route to the Goal4652/4653 app-level matrix with this correctness
   boundary and rerun the app-level scorecard.

Do not promote this as a broad app-level V4 speed claim before those gates.

## Non-Authorization

This goal does not authorize V4 release, broad V4 speedup wording, all-app
speedup wording, unrestricted exact Hausdorff claims, public true-zero-copy
claims, Tier-3 callback support, C ABI, embedding, non-Python host support, or
app-specific native kernels.
