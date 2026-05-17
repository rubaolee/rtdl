# Goal2308 Bounded Probe Coordinate-Scale Smoke

Date: 2026-05-17

## Purpose

Gemini's Goal2302/Goal2304 reviews accepted the bounded closed-shape point
probe with an important boundary: the fixed `0.5` half-length had only been
validated on the current RayJoin-exported coordinate scale.

This smoke test probes a narrower question: does the committed bounded probe
obviously fail on simple containing-shape examples at much smaller or much
larger coordinate magnitudes?

## Evidence

Artifact:

- `docs/reports/goal2308_bounded_probe_scale_smoke_pod_2026-05-17.json`

Pod:

- SSH: `root@69.30.85.202 -p 22064`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- Commit: `ec7f2dd5a11b2fa71b5609f097e52251ec7936d2d`
- Runtime source-tree style: `PYTHONPATH=src:.`

For each center coordinate, the test created one point at `(center, center)`
and one square closed shape containing that point. It then ran the prepared
`point_closed_shape_membership_2d_optix` count and row paths.

## Result

All synthetic rows matched the expected single positive membership:

| Center coordinate | Shape half-extent | Count | Rows |
| ---: | ---: | ---: | ---: |
| 0 | 1 | 1 | 1 |
| 1e-12 | 1 | 1 | 1 |
| 1e-9 | 1 | 1 | 1 |
| 1e-6 | 1 | 1 | 1 |
| 1e-3 | 1 | 1 | 1 |
| 1 | 1 | 1 | 1 |
| 1e3 | 1 | 1 | 1 |
| 1e6 | 10 | 1 | 1 |
| 1e8 | 1000 | 1 | 1 |
| 1e9 | 10000 | 1 | 1 |

## Interpretation

This smoke test reduces the immediate correctness concern for simple coordinate
magnitude shifts. It does not remove the broader boundary from Goal2301/Goal2303:
the fixed bounded-probe extent still needs broader data-shape and performance
evidence before it can be described as generally validated across coordinate
systems.

## Boundary

Accepted:

- Synthetic single-shape correctness smoke across the listed coordinate
  magnitudes.

Not claimed:

- No broad coordinate-scale validation.
- No broad performance validation.
- No RayJoin reproduction or RTDL-beats-RayJoin claim.
- No v2.0 release authorization.

