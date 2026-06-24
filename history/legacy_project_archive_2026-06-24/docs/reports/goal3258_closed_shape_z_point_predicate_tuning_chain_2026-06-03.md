# Goal3258: Closed-Shape Z-Point Predicate Tuning Chain

Date: 2026-06-03

## Purpose

Goals 3256 through 3258 respond to the Goal3255 AABB broadphase diagnostic.
Goal3255 showed that generic `AABB_INDEX_QUERY_2D point_contains` is fast
(`0.071144 ms`) and selective (`1542` AABB candidates for `1430` exact
positives), so the next question was whether the closed-shape membership path
could use the same tighter point-containing-AABB traversal while keeping exact
generic closed-shape semantics.

The chain is still app-agnostic. It changes only the generic OptiX
point/closed-shape membership predicate path:

- Goal3256 adds opt-in `RTDL_OPTIX_POINT_PRIMITIVE_QUERY_AXIS=z_point`.
- Goal3257 fuses boundary detection and ray-casting into one edge loop.
- Goal3258 removes per-edge `sqrtf` from the boundary check by comparing
  squared cross products.

RayJoin PIP remains the benchmark workload, not the native engine contract.

## Artifacts

- Goal3256 direct closed-shape JSON:
  `docs/reports/goal3256_closed_shape_z_point_probe_pod_2026-06-03.json`
- Goal3256 same-slice RayJoin JSON:
  `docs/reports/goal3256_rayjoin_z_point_same_slice_pod_2026-06-03.json`
- Goal3257 direct closed-shape JSON:
  `docs/reports/goal3257_closed_shape_z_point_single_pass_probe_pod_2026-06-03.json`
- Goal3257 same-slice RayJoin JSON:
  `docs/reports/goal3257_rayjoin_z_point_single_pass_same_slice_pod_2026-06-03.json`
- Goal3258 direct closed-shape JSON:
  `docs/reports/goal3258_closed_shape_z_point_squared_boundary_probe_pod_2026-06-03.json`
- Goal3258 same-slice RayJoin JSON:
  `docs/reports/goal3258_rayjoin_z_point_squared_boundary_same_slice_pod_2026-06-03.json`

Environment:

```text
GPU: NVIDIA A40, driver 570.211.01
RTDL_OPTIX_POINT_PRIMITIVE_QUERY_AXIS=z_point
RTDL_OPTIX_POINT_PRIMITIVE_QUERY_HALF_EXTENT=0.25
source_dirty: []
```

## Direct Closed-Shape Count

Dataset:

```text
/root/rtdl_goal3151/data/rayjoin_public_cdb/br_county_start0_count512.cdb
```

| Step | Commit | Exact count median | Device-filtered median | Count |
| --- | --- | ---: | ---: | ---: |
| Goal3254 per-probe count, vertical probe | `96ec7f14` | `0.883548 ms` | `0.782767 ms` | `1430` |
| Goal3256 z-point probe | `19363c88` | `0.661660 ms` | `0.556730 ms` | `1430` |
| Goal3257 single-pass predicate | `1e00d9d4` | `0.519359 ms` | `0.395635 ms` | `1430` |
| Goal3258 squared boundary predicate | `2ae2d6d4` | `0.416180 ms` | `0.314392 ms` | `1430` |

The direct device-filtered count improved `2.49x` versus the Goal3254
per-probe-count evidence (`0.782767 / 0.314392`), while matching exact count on
all samples.

## Same-Slice RayJoin Comparison

| Step | RayJoin PIP median | RTDL PIP median | RTDL / RayJoin | RTDL count |
| --- | ---: | ---: | ---: | ---: |
| Goal3248 current-best before device-filtered count | `0.193803 ms` | `0.934755 ms` | `4.82x` | `1430` |
| Goal3254 per-probe count | `0.193278 ms` | `0.794193 ms` | `4.11x` | `1430` |
| Goal3256 z-point probe | `0.204659 ms` | `0.548579 ms` | `2.68x` | `1430` |
| Goal3257 single-pass predicate | `0.206010 ms` | `0.396991 ms` | `1.93x` | `1430` |
| Goal3258 squared boundary predicate | `0.208473 ms` | `0.351587 ms` | `1.69x` | `1430` |

This is not yet `RTDL beats RayJoin`, and RayJoin still does not expose a PIP
positive-assignment count from the unpatched upstream binary. The comparison is
the same bounded public CDB slice and the same timing contract used in the
previous RayJoin reports.

## Interpretation

The chain confirms the Goal3255 diagnosis:

1. The broadphase itself is not the hard part on this slice.
2. The old vertical probe was doing unnecessary traversal work compared with a
   point-containing-AABB ray.
3. The exact point/closed-shape predicate was expensive because it walked every
   edge twice.
4. A per-edge square root in the inclusive boundary test was also measurable.

The best current RTDL PIP count path is therefore:

```text
z-point AABB traversal + exact device-side closed-shape predicate + no row materialization
```

The native operation remains generic: point/closed-shape membership over
generic IDs. The benchmark app chooses this path through an environment
specialization, but no RayJoin-specific names or contracts were added to the
native engine.

## Remaining Gap

After Goal3258, the same-slice PIP gap is `1.69x`. The dominant remaining native
phase is still the candidate count pass, now around `0.26 ms`.

Likely next work:

- Make the z-point axis path a documented first-class closed-shape membership
  mode rather than a private environment specialization, after review.
- Consider a prepared edge layout or warp-cooperative predicate evaluation to
  reduce the remaining per-candidate edge loop cost.
- Normalize the RayJoin benchmark runner so the chosen fast generic mode is
  explicit in artifacts rather than implicit in environment variables.

## Boundary

Goal3258 does not authorize release, public speedup claims, broad RT-core
speedup claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.

The accepted conclusion is narrower but strong: the generic RTDL
point/closed-shape path is now substantially closer to RayJoin on the bounded
PIP slice, moving from `4x+` slower to `1.69x` slower while preserving exact
count agreement with the exact prepared-count lane.
