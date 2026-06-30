# Goal3427 Prepared CuPy Refiner Timing

Status: implemented with pod artifact in
`docs/reports/goal3427_prepared_cupy_refiner_timing_probe_2026-06-04.json`.

## Purpose

Goal3424 made the closed-shape candidate stream exact after CuPy refinement by
carrying both public ids and input/prepared instance ordinals. The first timing
probe showed that correctness alone was not enough: native RT candidate
generation was fast, but the one-shot CuPy helper rebuilt and re-uploaded point,
shape, and vertex lookup arrays on every call.

Goal3427 adds a reusable partner helper:

```python
rt.prepare_closed_shape_membership_candidate_refiner_exact_cupy(points, shapes)
```

It prepares CuPy lookup columns once and then refines instance-aware candidate
streams without rebuilding those arrays.

## Pod Result

Full public RayJoin county CDB on NVIDIA RTX A5000:

| Path | Median seconds | Notes |
| --- | ---: | --- |
| Host exact prepared rows | 0.084061 | native RT candidates plus host exact refinement |
| RT candidate columns | 0.018988 | 47,570 conservative candidate rows |
| One-shot CuPy refine | 0.091222 | rebuilds/uploads lookup arrays per call |
| Prepared CuPy refine | 0.001425 | reuses resident point/shape/vertex lookup arrays |
| RT candidate + prepared CuPy refine | 0.020430 | 47,262 exact refined rows |

The prepared refiner made the refinement phase about `0.016x` the one-shot
refinement time, and the full candidate-plus-prepared-refine path was about
`0.243x` the host-exact median on this run. This is still a scoped benchmark
artifact, not a public speedup claim.

## Boundary

- This is partner-layer optimization over generic RTDL streams.
- It does not move RayJoin/CDB policy into the native engine.
- It does not authorize release, public speedup, RT-core speedup, true-zero-copy,
  or RayJoin paper-reproduction claims.
