# Goal 118: Segment/Polygon Linux Large-Scale Performance

Date: 2026-04-06
Status: accepted

## Purpose

Publish a clean Linux large-scale performance report for
`segment_polygon_hitcount` across the current backend surface, with explicit
PostGIS-backed correctness on large deterministic datasets.

This goal is not another feature-definition step. The family is already closed.
This goal makes the large Linux backend and PostGIS story reproducible from a
scripted clean-clone run.

## Required outcomes

1. a clean Linux script produces one machine-readable artifact bundle
2. the report includes:
   - `cpu`
   - `embree`
   - `optix`
   - `vulkan`
   - `postgis`
3. PostGIS-backed parity is shown on large deterministic datasets
4. prepared-path timing is reported where it is currently accepted
5. the final package states the current Vulkan honesty boundary directly

## Accepted dataset scale

- `derived/br_county_subset_segment_polygon_tiled_x64`
- `derived/br_county_subset_segment_polygon_tiled_x256`
- `derived/br_county_subset_segment_polygon_tiled_x512`
- `derived/br_county_subset_segment_polygon_tiled_x1024`

Prepared-path timing may stay on the smaller audited large rows:

- `x64`
- `x256`

## Accepted honesty boundary

This goal must not overclaim native RT-core maturity for this workload family.

If a backend is correct only through a fallback or oracle-backed path, the final
package must say that explicitly even if the timing numbers are still useful for
product reporting.

## Accepted package shape

- one goal report
- one machine-readable artifact bundle copied from the clean Linux run
- one explicit backend conclusion covering:
  - correctness vs PostGIS
  - current Linux timing position
  - prepared-path usefulness
  - remaining optimization gaps
