# Goal3247: Closed-Shape Probe Extent Tuning

Date: 2026-06-03

## Purpose

Goal3245 made the RTDL prepared OptiX LSI count path much faster, leaving PIP as
the dominant RayJoin same-slice gap. Goal3247 explores a generic PIP-adjacent
primitive question: can the prepared point/closed-shape membership probe use a
smaller bounded vertical segment without losing exact count parity on the public
RayJoin slice?

The code change does not change the default. The embedded OptiX PIP kernel still
uses `0.5f` unless the process sets:

```text
RTDL_OPTIX_POINT_PRIMITIVE_QUERY_HALF_EXTENT=<finite-positive-float>
```

The override is applied before NVRTC compiles the generic closed-shape
membership pipeline. It is not RayJoin-specific and does not add app vocabulary
or app logic to the native engine.

## Artifacts

- Code guard: `tests/goal3247_closed_shape_probe_extent_tuning_test.py`
- Sweep runner: `scripts/goal3247_closed_shape_probe_extent_sweep.py`
- Pod JSON: `docs/reports/goal3247_closed_shape_probe_extent_sweep_pod_2026-06-03.json`
- Pod stdout: `docs/reports/goal3247_closed_shape_probe_extent_sweep_pod_2026-06-03.stdout`

Pod evidence was collected on the same A40 pod and fresh commit
`dfd23f7d15999b8faf775b59cb869c104999aa2d`. The sweep artifact reports a clean
source tree.

## Result

Dataset:

```text
/root/rtdl_goal3151/data/rayjoin_public_cdb/br_county_start0_count512.cdb
```

Each extent ran in a separate Python process so the OptiX pipeline compiled with
the requested extent. Each row used one warmup and five measured repeats through
RTDL prepared OptiX PIP count.

| Probe half extent | Count samples | Median query | Candidate/write median | Status |
| --- | ---: | ---: | ---: | --- |
| default (`0.5`) | 1430 x 5 | 1.149502 ms | 0.950865 ms | count-preserving |
| `0.35` | 1430 x 5 | 1.229044 ms | 0.990494 ms | count-preserving but slower |
| `0.3` | 1430 x 5 | 1.016732 ms | 0.820243 ms | count-preserving |
| `0.275` | 1430 x 5 | 0.960659 ms | 0.760488 ms | count-preserving |
| `0.25` | 1430 x 5 | 0.936108 ms | 0.735469 ms | best count-preserving |
| `0.225` | 0 x 5 | 0.844805 ms | 0.744108 ms | rejected: misses hits |
| `0.2` | 0 x 5 | 0.862800 ms | 0.759639 ms | rejected: misses hits |
| `0.175` | 0 x 5 | 0.795880 ms | 0.672894 ms | rejected: misses hits |
| `0.15` | 0 x 5 | 0.661362 ms | 0.563590 ms | rejected: misses hits |
| `0.125` | 0 x 5 | 0.580782 ms | 0.483860 ms | rejected: misses hits |

The best safe value in this sweep is `0.25`, which improves the same-slice PIP
count path by `1.23x` over the default (`1.149502 ms` to `0.936108 ms`) while
preserving the default exact count of `1430`.

Using the Goal3245 RayJoin PIP query median (`0.193596 ms`), the tuned RTDL PIP path is still about 4.84x slower than RayJoin on this bounded same-slice comparison. Goal3247 is therefore useful tuning, not a complete RayJoin-level solution.

## Interpretation

The sweep shows that the hardcoded `0.5` probe was conservative for this public
slice. A smaller `0.25` probe reduces AABB traversal work and candidate/write
time without changing the result. But the cliff between `0.25` and `0.225` is
sharp: below `0.25`, the current OptiX AABB/probe interaction misses all hits on
this slice.

So the safe next design is not "make `0.25` universal." It is either:

- a caller-controlled generic probe-extent option with validation against the
  default/exact route for a given workload, or
- a stronger generic primitive that does not rely on this extent heuristic, such
  as device-resident grouped ray/segment parity/count.

The second option is the larger RayJoin-level path because the old
ray/segment-group parity route was correct but slow: it materialized segment
intersection rows and grouped them on the host.

## Boundary

Goal3247 does not authorize release, public speedup claims, broad RT-core
speedup claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.

The narrow claim is only that, on the measured public same-slice PIP count
workload, a `0.25` closed-shape probe extent preserves the current count and
reduces RTDL prepared OptiX PIP query time by about `1.23x`.
