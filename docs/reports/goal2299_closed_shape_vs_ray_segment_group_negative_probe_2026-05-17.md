# Goal2299: Closed-Shape Versus Ray/Segment Group Negative Probe

Status: rejected fallback path.

## Purpose

Goal2295 showed that prepared closed-shape membership still spends most of its
native time in candidate traversal/write. Goal2299 checks whether the older
generic ray/segment group-count primitive is a better route for RayJoin-style
PIP when both sides use prepared static geometry and prepacked query inputs.

## Evidence

Artifact:
`docs/reports/goal2299_pip_closed_shape_vs_ray_segment_group_probe_pod_2026-05-17.json`

Environment:

- Pod SSH: `root@69.30.85.202 -p 22064`
- Commit: `419b4a6e`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- Query stream:
  `/root/goal2198_rayjoin_same_query_pod_r6/artifacts/rayjoin_pip_gen100000_stream.json`
- Query count: 100,000
- Closed shapes: 15,700
- Boundary segments for ray/segment path: 341,048

## Results

| Route | Median Seconds | Rows | Correctness |
| --- | ---: | ---: | --- |
| Prepared closed-shape positive rows | 0.055879781 | 8,686 | reference set |
| Prepared closed-shape scalar count | 0.042318612 | 8,686 | count matches |
| Prepared ray/segment odd parity | 3.145604309 | 8,686 | exact set match |

The ray/segment odd-parity route is correct but much slower:

- `56.29x` slower than closed-shape row return;
- `74.33x` slower than closed-shape scalar count.

## Interpretation

The closed-shape membership primitive is the right current primitive family for
this workload. Re-expressing PIP as boundary-segment ray crossings gives an
app-agnostic formulation, but it explodes the static scene to 341,048 boundary
segments and loses badly.

The next optimization should improve closed-shape membership directly:

- reduce candidate traversal/write work;
- improve device-side closed-shape filtering;
- or move exact continuation/output handling closer to the device or partner
  layer.

It should not route the current RayJoin-style PIP path back through boundary
segment crossings.

## Boundary

This report does not authorize:

- a PIP speedup claim;
- RayJoin paper reproduction;
- RTDL beats RayJoin;
- broad closed-shape claims;
- true zero-copy;
- v2.0 release readiness.

The only accepted lesson is that the ray/segment group odd-parity route is a
correct but poor performance fallback for the tested RayJoin-exported PIP
stream.
