# Goal3254: Closed-Shape Per-Probe Count Accumulation Pod Evidence

Date: 2026-06-03

## Purpose

Goal3254 tests a narrow generic OptiX optimization for prepared
point/closed-shape membership count-only queries.

Before this goal, positive-hit count-only mode used a global `atomicAdd` for
each accepted hit in the any-hit program. Goal3254 changes that count-only path
to accumulate accepted hits in OptiX payload register `p2` for each probe ray,
then perform one global `atomicAdd` per probe in raygen after traversal.

This remains a generic point/closed-shape membership optimization. It does not
add RayJoin-specific ABI, naming, or policy to the native engine.

## Artifacts

- Direct count probe JSON:
  `docs/reports/goal3254_closed_shape_per_probe_count_probe_pod_2026-06-03.json`
- Direct count probe stdout:
  `docs/reports/goal3254_closed_shape_per_probe_count_probe_pod_2026-06-03.stdout`
- Same-slice comparison JSON:
  `docs/reports/goal3254_rayjoin_per_probe_count_pod_2026-06-03.json`
- Same-slice comparison stdout:
  `docs/reports/goal3254_rayjoin_per_probe_count_pod_2026-06-03.stdout`

Environment:

```text
GPU: NVIDIA A40, driver 570.211.01
RTDL commit: 96ec7f141691cee1a3988eee2bcaa8b7be911f82
RTDL_OPTIX_POINT_PRIMITIVE_QUERY_HALF_EXTENT=0.25
```

Both pod JSON artifacts report clean source state:

```text
source_dirty: []
```

The pod rebuilt `build/librtdl_optix.so` after the native kernel change and ran
the focused static tests:

```text
Ran 9 tests in 0.007s
OK
```

## Direct Count Result

Dataset:

```text
/root/rtdl_goal3151/data/rayjoin_public_cdb/br_county_start0_count512.cdb
```

| Route | Median query | Counts | Status |
| --- | ---: | ---: | --- |
| Exact prepared closed-shape count | `0.883548 ms` | `1430 x 9` | exact authority |
| Device-filtered per-probe count | `0.782767 ms` | `1430 x 9` | matches exact on this slice |

The device-filtered route is `1.13x` faster than exact count on this direct
probe, but only slightly faster than Goal3252's pre-Goal3254 device-filtered
median of `0.785675 ms`.

## Same-Slice Comparison

| Workload | RayJoin median | RTDL median | RTDL / RayJoin | Count contract |
| --- | ---: | ---: | ---: | --- |
| LSI | `0.234127 ms` | `0.464335 ms` | `1.98x` | visible count matches: `269` vs `269` |
| PIP | `0.193278 ms` | `0.794193 ms` | `4.11x` | RTDL count `1430`; RayJoin PIP count not printed |

For PIP, the exact-validation lane median was:

```text
validation_exact_query_ms median = 0.933329 ms
```

Native phase telemetry confirms the count-only path still avoids materialized
rows:

```text
mode = device_filtered_count
candidate_write_pass = 0
candidate_download = 0
exact_refine = 0
raw_candidate_count = emitted_count = 1430
```

## Interpretation

Goal3254 is a valid generic optimization, but it does not materially close the
RayJoin PIP gap. Reducing global atomics from per-hit to per-probe gives only a
small improvement. The measured dominant cost remains the OptiX traversal plus
device-side closed-shape predicate work: the PIP native `candidate_count_pass`
still sits around `0.72 ms`.

The diagnostic conclusion is now stronger: the remaining PIP/RayJoin gap is not
mostly host row materialization, host exact refinement, or global count atomic
contention. The next meaningful optimization needs a stronger generic
closed-shape membership/count design, such as better prepared-shape indexing,
lower-cost shape membership predicates, or a different generic closed-shape
count primitive.

## Boundary

Goal3254 does not authorize release, public speedup claims, broad RT-core
speedup claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.

The accepted conclusion is diagnostic: per-probe count accumulation is correct
and modestly useful, but insufficient. The next improvement must target the
generic closed-shape traversal/predicate cost itself.
