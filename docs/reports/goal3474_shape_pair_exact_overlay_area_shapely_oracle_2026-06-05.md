# Goal3474 - Exact Overlay-Area Oracle for Shape-Pair Relation Rows

## Status

Implemented locally; pod artifact pending.

## Purpose

Goal3474 adds a correctness oracle for the hardest remaining Spatial RayJoin
gap. Goals3470-3472 showed that the convex fast path is exact only for 168 of
4,543 public-CDB active relation rows. The remaining rows are mostly nonconvex
and need a generic simple-polygon overlay-area continuation.

This goal does not add that runtime primitive. Instead, it computes exact
intersection areas for the same RTDL/OptiX active relation rows using
Shapely/GEOS on CPU. That gives the future GPU continuation a concrete oracle
target.

## Implementation

The script is:

- `scripts/goal3474_shape_pair_exact_overlay_area_shapely_oracle.py`

It:

1. loads the same public-CDB shape pair used by Goals3467 and 3471;
2. uses the existing RTDL/OptiX prepared shape-pair relation stream to select
   active rows;
3. copies only the generic zero-based ordinal columns to host;
4. builds Shapely/GEOS polygons as an external CPU oracle;
5. computes exact `left_polygon.intersection(right_polygon).area` for every
   active relation row;
6. records timing, total area, positive-row counts, geometry repair status, and
   any topology exceptions.

## Boundary

Shapely is optional external oracle tooling, not an RTDL runtime dependency and
not a performance path. This report does not authorize release, public speedup
wording, broad RT-core speedup wording, true-zero-copy wording, RayJoin paper
reproduction claims, RTDL-beats-RayJoin claims, or full overlay-area completion
claims.

## Expected Use

Run on a pod after installing the optional oracle dependency:

```bash
python -m pip install shapely
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY="$PWD/build/librtdl_optix.so" \
  python scripts/goal3474_shape_pair_exact_overlay_area_shapely_oracle.py \
  --iterations 2 \
  --output docs/reports/goal3474_shape_pair_exact_overlay_area_shapely_oracle_pod_2026-06-05.json
```

The resulting artifact should be read as a correctness target for the future
generic simple-polygon overlay-area continuation, not as RTDL performance evidence.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3474_shape_pair_exact_overlay_area_shapely_oracle_test`
