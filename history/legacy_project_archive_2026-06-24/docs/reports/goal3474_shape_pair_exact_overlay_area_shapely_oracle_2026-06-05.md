# Goal3474 - Exact Overlay-Area Oracle for Shape-Pair Relation Rows

## Status

Implemented with pod artifact.

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

## Pod Evidence

Pod command ran on `root@69.30.85.203 -p 22057` with repository commit
`a03753b302511e1c39f4f392a1e9bd0d694b6c79`, `NVIDIA RTX A5000,
580.126.09`, and Shapely `2.1.2` installed in an isolated
`.venv_goal3474` venv with `--system-site-packages`.

Artifact:

- `docs/reports/goal3474_shape_pair_exact_overlay_area_shapely_oracle_pod_2026-06-05.json`

Key results:

| Measure | Value |
| --- | ---: |
| active relation rows | 4,543 |
| positive exact-area rows | 1,090 |
| zero exact-area rows | 3,453 |
| topology/oracle exceptions | 0 |
| total exact overlay area | 26.08321766231042 |
| max exact row area | 1.5951731790844415 |
| synthetic 1.0-area fixture error | 0.0 |
| geometry build time | 5.570154648274183 s |
| Shapely exact-oracle median time | 0.4146229340694845 s |
| RTDL/OptiX relation steady min time | 0.004817125387489796 s |
| ordinal host-copy median time | 0.0005348655395209789 s |

Geometry validity/repair counts:

| Side | valid | make_valid |
| --- | ---: | ---: |
| left | 5,777 | 9,923 |
| right | 353 | 596 |

Interpretation: the future generic simple-polygon overlay-area continuation now
has an exact per-row correctness target for the public-CDB active relation
stream. This artifact also shows why the convex-only route cannot close the
benchmark: the exact oracle finds 1,090 positive-area rows, while Goal3471's
convex fast path supports only 168 rows and contributes only
0.05788295450020087 area.

## Expected Use

Run on a pod after installing the optional oracle dependency:

```bash
python -m venv --system-site-packages .venv_goal3474
.venv_goal3474/bin/python -m pip install shapely
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY="$PWD/build/librtdl_optix.so" \
  .venv_goal3474/bin/python scripts/goal3474_shape_pair_exact_overlay_area_shapely_oracle.py \
  --iterations 2 \
  --progress-every 500 \
  --output docs/reports/goal3474_shape_pair_exact_overlay_area_shapely_oracle_pod_2026-06-05.json
```

The resulting artifact should be read as a correctness target for the future
generic simple-polygon overlay-area continuation, not as RTDL performance evidence.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3474_shape_pair_exact_overlay_area_shapely_oracle_test`

Pod validation:

- `PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so .venv_goal3474/bin/python scripts/goal3474_shape_pair_exact_overlay_area_shapely_oracle.py --iterations 2 --progress-every 500 --output docs/reports/goal3474_shape_pair_exact_overlay_area_shapely_oracle_pod_2026-06-05.json`
