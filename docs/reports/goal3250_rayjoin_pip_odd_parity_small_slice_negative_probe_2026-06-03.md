# Goal3250: RayJoin PIP Odd-Parity Small-Slice Negative Probe

Date: 2026-06-03

## Purpose

Goal3248 left the RayJoin PIP count row as the largest same-slice gap:
prepared closed-shape membership with
`RTDL_OPTIX_POINT_PRIMITIVE_QUERY_HALF_EXTENT=0.25` measured about `0.935 ms`
against upstream RayJoin's `0.194 ms`.

Before adding a new dense device-resident grouped parity/count primitive, this
goal rechecked the older generic prepared ray/segment group odd-parity route on
the same bounded 512-chain PIP slice. The question was simple: can that older
primitive be reused as a short-term PIP route at small scale?

## Artifacts

- Probe runner:
  `scripts/goal3250_rayjoin_pip_odd_parity_small_slice_probe.py`
- Pod JSON:
  `docs/reports/goal3250_rayjoin_pip_odd_parity_small_slice_probe_pod_2026-06-03.json`
- Pod stdout:
  `docs/reports/goal3250_rayjoin_pip_odd_parity_small_slice_probe_pod_2026-06-03.stdout`

The clean pod run used commit `76bfa25ca2a03fc68791c7ba2cb6e89f5b67cb99` and
reported `source_dirty: []`.

## Result

Dataset:

```text
/root/rtdl_goal3151/data/rayjoin_public_cdb/br_county_start0_count512.cdb
```

The runner converts the 481 closed shapes into 25,330 generic boundary segments
and casts one horizontal generic ray per query point. Native code sees only
rays, segments, and caller-owned integer group ids.

| Route | Median query | Rows/count | Correctness against closed-shape reference |
| --- | ---: | ---: | --- |
| Prepared closed-shape membership count | `0.920307 ms` | `1430` | reference |
| Prepared ray/segment odd parity | `2.948057 ms` | `123` | fails: misses `1307`, extras `0` |

The odd-parity route is `3.20x` slower than the prepared closed-shape count and
does not match the inclusive closed-shape positive-hit set on this CDB probe
slice.

## Interpretation

The old ray/segment group odd-parity route remains rejected for RayJoin-style
PIP. Goal2299 already showed it was exact but much slower on a 100K generated
query stream. Goal3250 shows a different small-slice failure mode: the bounded
CDB probe points include boundary-inclusive positives, while the generic
horizontal ray parity formulation returns only 123 of the 1430 closed-shape
positive rows.

Making this route correct would require extra app-level boundary-membership
policy before or beside parity. Even if that correctness layer were added, this
small run is already slower than the current prepared closed-shape path.

So the next RayJoin PIP target should not be "reuse odd parity." It should be a
stronger generic membership/count primitive, or a device-resident grouped
continuation that can accumulate the needed membership/count result without
materializing a large row stream or pushing boundary-specific policy into the
native engine.

## Boundary

Goal3250 does not authorize release, public speedup claims, broad RT-core
speedup claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.

The narrow conclusion is negative: the existing prepared ray/segment odd-parity
route is neither correct for this inclusive CDB PIP slice nor competitive with
the current closed-shape membership primitive.
