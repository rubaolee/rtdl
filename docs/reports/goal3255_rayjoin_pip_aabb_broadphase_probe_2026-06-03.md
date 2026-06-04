# Goal3255: RayJoin PIP AABB Broadphase Probe

Date: 2026-06-03

## Purpose

Goal3255 measures whether the existing generic OptiX
`AABB_INDEX_QUERY_2D point_contains` primitive can serve as a useful broadphase
for the RayJoin PIP gap.

This is a diagnostic measurement only. AABB point containment is not exact
point-in-polygon or closed-shape membership. It can only identify candidate
shape boxes that contain query points. Exact app semantics still require a
separate generic predicate or caller-owned continuation.

## Artifact

- Pod JSON:
  `docs/reports/goal3255_rayjoin_pip_aabb_broadphase_probe_pod_2026-06-03.json`

Environment:

```text
GPU: NVIDIA A40, driver 570.211.01
RTDL commit: eea2f7b6e1ec676ce6860b5ac0953dba0e254ce0
RTDL_OPTIX_POINT_PRIMITIVE_QUERY_HALF_EXTENT=0.25
source_dirty: []
```

The pod also ran the Goal3255 static test:

```text
Ran 3 tests in 0.006s
OK
```

## Dataset

```text
/root/rtdl_goal3151/data/rayjoin_public_cdb/br_county_start0_count512.cdb
```

Input shape:

```text
points: 512
closed shapes: 481
AABB boxes: 481
```

## Result

| Route | Median query | Count | Meaning |
| --- | ---: | ---: | --- |
| Generic AABB point_contains | `0.071144 ms` | `1542` | broadphase candidates only |
| Generic closed-shape device-filtered count | `0.780968 ms` | `1430` | exact positive membership on this slice |

Derived ratios:

```text
AABB candidate / exact positive count = 1.078x
AABB time / closed-shape time = 0.091x
```

## Interpretation

This is a useful positive diagnostic. The existing generic AABB primitive is
about `11x` faster than the current exact closed-shape count on this same PIP
slice, and the candidate inflation is low: `1542` broadphase candidates versus
`1430` exact positives.

That means a broadphase-first design is worth pursuing. It does not mean AABB
can replace exact PIP. The current primitive answers "which point/box pairs
overlap?" not "which point/closed-shape pairs are inside?".

The likely next engineering target is therefore a generic device-resident
candidate-to-predicate continuation:

1. Use `AABB_INDEX_QUERY_2D point_contains` to produce a compact candidate
   stream.
2. Keep that stream on device.
3. Apply a generic exact point/closed-shape predicate to each candidate.
4. Reduce counts or emit bounded witness rows without host materialization.

This target is still app-agnostic because it is phrased as point/box candidate
generation plus exact closed-shape membership over generic IDs. RayJoin remains
only the benchmark application that revealed the need.

## Boundary

Goal3255 does not authorize release, public speedup claims, broad RT-core
speedup claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.

The accepted conclusion is narrow: existing AABB broadphase is fast enough and
selective enough on the current PIP slice to justify building a generic
device-resident candidate-to-predicate continuation.
