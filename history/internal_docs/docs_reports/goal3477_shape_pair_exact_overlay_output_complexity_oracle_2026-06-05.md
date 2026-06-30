# Goal3477 - Exact Overlay Output-Complexity Oracle

## Status

Implemented with pod artifact.

## Purpose

Goal3474 established an exact area total for the public-CDB active relation
stream. Goal3477 asks the next engineering question: if RTDL implements a
generic GPU simple-polygon overlay continuation, does it need to output full intersection geometry,
or is a scalar exact-area continuation enough for the current benchmark target?

The answer affects the runtime contract:

- scalar area only: a bounded grouped reduction continuation may be sufficient;
- full overlay geometry: the runtime needs a streamed output-geometry contract
  with component, vertex, and ownership metadata.

## Implementation

The script is:

- `scripts/goal3477_shape_pair_exact_overlay_output_complexity_oracle.py`

It reuses the Goal3474 external Shapely/GEOS oracle setup, consumes the same
RTDL/OptiX active relation ordinal stream, and records geometry-type counts,
positive-row counts, empty/touch-only rows, component counts, output vertex
counts, and max-complexity samples.

## Pod Evidence

Pod command ran on `root@69.30.85.203 -p 22057` with repository commit
`85ff57ff058e9130c9760d94e69434ee24f5e191`, `NVIDIA RTX A5000,
580.126.09`, and Shapely `2.1.2` in the Goal3474 oracle venv.

Artifact:

- `docs/reports/goal3477_shape_pair_exact_overlay_output_complexity_oracle_pod_2026-06-05.json`

Key results:

| Measure | Value |
| --- | ---: |
| active relation rows | 4,543 |
| positive exact-area rows | 1,090 |
| empty exact-intersection rows | 1 |
| boundary-only/touch rows | 3,452 |
| topology/oracle exceptions | 0 |
| total exact area | 26.083217662310428 |
| total polygon components in exact outputs | 2,801 |
| total output vertices in exact outputs | 42,314 |
| max polygon components in one row | 22 |
| max output vertices in one row | 586 |
| Shapely output-complexity oracle time | 0.6810975121334195 s |

Geometry-type counts over all active relation rows:

| Geometry type | Rows |
| --- | ---: |
| `Point` | 3,452 |
| `Polygon` | 434 |
| `MultiPolygon` | 609 |
| `GeometryCollection` | 48 |

Positive-area geometry-type counts:

| Geometry type | Rows |
| --- | ---: |
| `Polygon` | 433 |
| `MultiPolygon` | 609 |
| `GeometryCollection` | 48 |

The max-output sample is row 184, a `MultiPolygon` with 11 polygon components
and 586 output vertices. This supports a scalar exact-area continuation as the
near-term benchmark target, but it also shows that a full overlay-geometry
contract would need streamed component/vertex output rather than a single fixed
row per relation pair.

## Boundary

This is external CPU oracle evidence, not an RTDL runtime dependency and not a
performance path. It does not authorize release, public speedup wording, broad
RT-core speedup wording, true-zero-copy wording, RayJoin paper reproduction
claims, RTDL-beats-RayJoin claims, or full exact overlay-area completion claims.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3477_shape_pair_exact_overlay_output_complexity_oracle_test`

Pod validation:

- `PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so .venv_goal3474/bin/python scripts/goal3477_shape_pair_exact_overlay_output_complexity_oracle.py --iterations 1 --progress-every 500 --output docs/reports/goal3477_shape_pair_exact_overlay_output_complexity_oracle_pod_2026-06-05.json`
