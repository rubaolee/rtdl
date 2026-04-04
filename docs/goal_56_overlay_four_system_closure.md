# Goal 56 Overlay Four-System Closure

## Objective

Close the first accepted bounded four-system result for the `overlay` workload
across:

- PostGIS
- native C oracle
- Embree
- OptiX

This goal should use an already accepted bounded real-data package rather than
introducing a new dataset family.

## Why This Goal

Current accepted bounded four-system coverage is strong for:

- `lsi`
- `pip`

across:

- `County ⊲⊳ Zipcode`
- `BlockGroup ⊲⊳ WaterBodies`
- bounded `LKAU ⊲⊳ PKAU`

But the RayJoin-style artifact surface still has a major gap:

- Table 4
- Figure 15

Those are overlay-focused, and the repo still lacks an accepted bounded
four-system `overlay` result.

## Accepted First Package

The first package for this goal is:

- bounded `LKAU ⊲⊳ PKAU`
- source boundary: Goal 37 / Goal 54 `sunshine_tiny`

Why this package is first:

- it is already four-system closed for `lsi` and `pip`
- it is polygon-vs-polygon, which matches current `overlay` input shape
- it is small enough to debug exact seed semantics without the cost of larger
  packages
- it is already an accepted bounded RayJoin-family slice

## Main Technical Requirement

Before implementation is accepted, this goal must define exactly what
"correct vs PostGIS" means for overlay.

That comparison rule must be explicit and stable before execution.

Accepted comparison surface for this goal:

- exact-row parity on the current RTDL `overlay-seed analogue` row schema:
  - `left_polygon_id`
  - `right_polygon_id`
  - `requires_lsi`
  - `requires_pip`

The goal does not compare:

- full polygon overlay materialization
- `ST_Intersection` output geometry

PostGIS truth must be derived as the same seed analogue:

- `requires_lsi = 1` iff the polygon pair has at least one RTDL-style indexed
  segment intersection
- `requires_pip = 1` iff the first vertex of either polygon is covered by the
  other polygon
- final comparison surface is the full left × right polygon pair matrix with
  the two derived flags

## Acceptance

Goal 56 is accepted only if:

1. the bounded `LKAU ⊲⊳ PKAU` package is used explicitly
2. the overlay correctness comparison rule is defined before execution
3. PostGIS uses an indexed and professionally structured query path where
   applicable
4. the bounded result is validated across:
   - PostGIS
   - native C oracle
   - Embree
   - OptiX
5. the final report updates the project’s bounded reproduction position for
   Table 4 / Figure 15
6. at least 2 AIs approve before publication
