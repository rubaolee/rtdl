# Goal 120 OptiX Segment/Polygon Native Promotion

Date: 2026-04-06
Status: accepted

## Summary

Goal 120 switched `segment_polygon_hitcount` on OptiX from exact host-side
nested-loop counting to the dormant OptiX custom-AABB traversal path that was
already present in the native backend.

The result is:

- OptiX now really uses native custom-primitive traversal for this family
- parity stayed clean on the accepted closure cases
- large deterministic PostGIS parity stayed clean on Linux
- but the measured performance did **not** materially improve

So Goal 120 closes as:

- a native-promotion success for the OptiX implementation path
- but **not** as a performance breakthrough

## What Changed

Changed file:

- [rtdl_optix.cpp](/Users/rl2025/rtdl_python_only/src/native/rtdl_optix.cpp)

Previous behavior:

- `run_seg_poly_hitcount_optix(...)` allocated output rows and counted polygon
  hits through an exact host-side nested loop

Current behavior:

- the OptiX path now builds polygon AABB acceleration
- uploads segments, polygons, and vertex buffers
- launches the native `__raygen__segpoly_probe` / `__intersection__segpoly_isect`
  / `__anyhit__segpoly_anyhit` pipeline
- reads back one `(segment_id, hit_count)` row per segment

This means the OptiX backend is no longer only claiming a future traversal
shape for this family. It now actually uses one.

## Correctness Result

Clean Linux closure run:

```bash
cd /home/lestat/work/rtdl_goal118_clean
PYTHONPATH=src:. python3 -m unittest tests.goal110_segment_polygon_hitcount_closure_test
```

Accepted result:

- `5` tests
- `OK`

This confirms parity stayed clean for the accepted authored, fixture, derived,
and prepared OptiX closure surface.

## Large Linux/PostGIS Result

Large Linux/PostGIS rerun:

```bash
cd /home/lestat/work/rtdl_goal118_clean
PYTHONPATH=src:. python3 scripts/goal118_segment_polygon_linux_large_perf.py \
  --db-name rtdl_postgis \
  --perf-iterations 3 \
  --output-dir build/goal120_try
```

Accepted result:

- large deterministic PostGIS parity stayed clean through `x1024`
- OptiX remained parity-clean on:
  - `x64`
  - `x256`
  - `x512`
  - `x1024`

## Performance Reading

### Current-run mean comparison vs Goal 118

| Dataset | Goal 118 OptiX mean (s) | Goal 120 OptiX mean (s) |
| --- | ---: | ---: |
| `x64` | `0.024139` | `0.024354` |
| `x256` | `0.376711` | `0.378534` |

Large PostGIS-backed rows after Goal 120:

| Dataset | PostGIS (s) | OptiX (s) |
| --- | ---: | ---: |
| `x64` | `0.008962` | `0.029681` |
| `x256` | `0.050481` | `0.383164` |
| `x512` | `0.099124` | `1.506938` |
| `x1024` | `0.311981` | `6.001533` |

Interpretation:

- the new OptiX path is real
- but the measured timings are effectively unchanged within noise
- RTDL remains far slower than PostGIS on these large deterministic rows

## Why The Speed Did Not Improve

The native promotion changed *where* the work runs, but not enough of the
overall algorithmic cost structure.

The current OptiX native path still does expensive exact segment-vs-polygon
logic in the intersection program itself.

So although traversal is now native:

- the workload still does not get a strong selective candidate-stage advantage
- the overall cost still behaves too much like exact per-candidate work

In other words:

- architecture improved
- asymptotic/performance story did not

## Final Conclusion

Goal 120 is worth keeping, but it does **not** solve the slowness problem.

What it accomplished:

- OptiX now truly owns a native traversal path for
  `segment_polygon_hitcount`
- parity remained clean
- large PostGIS parity remained clean

What it did not accomplish:

- a meaningful speedup
- competitiveness with PostGIS

So the next decision point is now sharper:

- keep this architectural improvement
- but only continue if you want a deeper redesign aimed at
  candidate-generation selectivity rather than merely moving the same exact work
  onto the GPU

## Artifacts

- machine-readable rerun summary:
  - [goal120 artifact JSON](goal120_optix_segment_polygon_native_promotion_artifacts_2026-04-06/summary.json)
- rendered rerun summary:
  - [goal120 artifact Markdown](goal120_optix_segment_polygon_native_promotion_artifacts_2026-04-06/summary.md)
