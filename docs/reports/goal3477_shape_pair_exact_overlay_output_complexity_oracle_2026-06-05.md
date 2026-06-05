# Goal3477 - Exact Overlay Output-Complexity Oracle

## Status

Implemented locally; pod artifact pending.

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

## Boundary

This is external CPU oracle evidence, not an RTDL runtime dependency and not a
performance path. It does not authorize release, public speedup wording, broad
RT-core speedup wording, true-zero-copy wording, RayJoin paper reproduction
claims, RTDL-beats-RayJoin claims, or full exact overlay-area completion claims.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3477_shape_pair_exact_overlay_output_complexity_oracle_test`
