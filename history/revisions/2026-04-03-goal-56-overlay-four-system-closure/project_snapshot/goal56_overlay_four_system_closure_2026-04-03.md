# Goal 56 LKAU PKAU Overlay Four-System Closure

Date: 2026-04-03

## Scope

This round closes the first bounded four-system `overlay` result for RTDL on an
accepted RayJoin-family package.

Bounded package:

- `LKAU ⊲⊳ PKAU`
- Goal 37 / Goal 54 `sunshine_tiny`

Compared systems:

- PostGIS
- native C oracle
- Embree
- OptiX

Backend label note:

- the Goal 56 harness records the oracle backend as `cpu`
- in this report, that same backend is described as the native C oracle

Important fidelity boundary:

- this is an `overlay-seed analogue`
- it is not full polygon overlay materialization
- the exact comparison surface is the current RTDL seed row schema:
  - `left_polygon_id`
  - `right_polygon_id`
  - `requires_lsi`
  - `requires_pip`

Acceptance evidence boundary:

- the accepted closure in this report is based on the bounded remote execution
  artifact produced on `192.168.1.20`
- the local `goal56_overlay_four_system_test.py` file validates harness
  contract pieces such as SQL/index-use structure and exact-row hash helpers
- it does not by itself reproduce the remote four-system result locally

## PostGIS Truth Contract

PostGIS truth was derived to match RTDL’s current overlay-seed semantics rather
than generic `ST_Intersection` output geometry.

Derived seed flags:

- `requires_lsi = 1`
  - iff the polygon pair has at least one RTDL-style indexed boundary segment
    intersection
- `requires_pip = 1`
  - iff the first vertex of either polygon is covered by the other polygon

Final PostGIS comparison surface:

- full left × right polygon pair matrix
- exact rows on:
  - `left_polygon_id`
  - `right_polygon_id`
  - `requires_lsi`
  - `requires_pip`

## Input Summary

- host: `192.168.1.20`
- bbox label: `sunshine_tiny`
- bbox: `-26.72,152.95,-26.55,153.10`
- lakes source elements: `280`
- lakes closed ways: `280`
- lakes features: `280`
- parks source elements: `264`
- parks closed ways: `264`
- parks features: `264`
- PostGIS load sec: `0.304573762`

## Indexed PostGIS Plans

- `requires_lsi` positive-pair derivation used index: `true`
- `requires_pip` positive-pair derivation used index: `true`
- final overlay-seed full-pair query used index: `true`

PostGIS plan timing summary:

- `lsi` seed plan execution: `66.211 ms`
- `pip` seed plan execution: `7.970 ms`
- final overlay-seed query execution: `137.947 ms`

## Results

PostGIS overlay-seed truth:

- rows: `73920`
- sha256: `25debd83ee7f4bf750c787a2c991af2d9a9d9e2c99af28e38877b52fcf7f618e`
- sec: `0.228491376`

RTDL parity:

- C oracle
  - parity vs PostGIS: `true`
  - rows: `73920`
  - sha256: `25debd83ee7f4bf750c787a2c991af2d9a9d9e2c99af28e38877b52fcf7f618e`
  - sec: `5.144722894`
- Embree
  - parity vs PostGIS: `true`
  - rows: `73920`
  - sha256: `25debd83ee7f4bf750c787a2c991af2d9a9d9e2c99af28e38877b52fcf7f618e`
  - sec: `0.085036251`
- OptiX
  - parity vs PostGIS: `true`
  - rows: `73920`
  - sha256: `25debd83ee7f4bf750c787a2c991af2d9a9d9e2c99af28e38877b52fcf7f618e`
  - sec: `0.567442065`

## Important Fixes During Goal 56

Two OptiX overlay fixes were required before the bounded package closed:

1. The OptiX overlay `requires_pip` supplement was still using a manual
   point-in-polygon helper while the rest of the project had already moved to
   the exact GEOS-backed `covers(...)` path where available.
2. That same OptiX overlay supplement downcast first-vertex coordinates to
   `float`, which caused two remaining boundary-case false negatives on the
   Australia slice.

After switching OptiX overlay to the exact predicate family and preserving
first-vertex coordinates as `double`, the bounded package became parity-clean.

Important implementation boundary:

- this accepted OptiX closure was observed on a GEOS-enabled OptiX build on
  `192.168.1.20`
- when `RTDL_OPTIX_HAS_GEOS` is not available, the source still falls back to
  the manual exact-point predicate path
- so the accepted result here is a claim about the validated bounded run on
  that host configuration, not a blanket claim about every possible OptiX build

## Conclusion

Goal 56 closes the first accepted bounded four-system `overlay-seed analogue`
for RTDL on a RayJoin-family package.

Accepted bounded closure:

- `LKAU ⊲⊳ PKAU`
- PostGIS == C oracle == Embree == OptiX

This improves the project’s bounded reproduction position for:

- Table 4
- Figure 15

It does not claim:

- full polygon overlay materialization
- continent-scale `LKAU ⊲⊳ PKAU`
- full lakes/parks family closure
