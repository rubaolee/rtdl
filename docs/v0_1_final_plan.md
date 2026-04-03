# RTDL v0.1 Plan

## Definition

RTDL v0.1 is the first serious vertical slice of the broader project vision.

It is not “all of RTDL.” It is the first bounded proof that the project can:

- express RayJoin-style workloads in the DSL
- preserve a trustworthy correctness baseline
- run those workloads on more than one backend
- support a reproducible experiment/reporting workflow

## What v0.1 Means Today

Current v0.1 scope:

- application family: RayJoin-style spatial join workloads
- language surface: six current RTDL workloads
- oracle: native C/C++ ground-truth path
- backends:
  - Embree on CPU
  - OptiX on NVIDIA GPU
- external checker:
  - indexed PostGIS comparison on the Linux validation host

## What Is Already Complete

### Core language/runtime baseline

- Python-hosted kernel authoring surface
- compiler IR and lowering
- current workload coverage:
  - `lsi`
  - `pip`
  - `overlay`
  - `ray_tri_hitcount`
  - `segment_polygon_hitcount`
  - `point_nearest_segment`

### Correctness baseline

- native C/C++ oracle is in place
- old Python oracle remains available for regression checks
- cross-checking exists across:
  - Python oracle
  - native oracle
  - Embree
  - OptiX on validated bounded targets

### Embree path

- mature controlled CPU backend
- real-data validation on Linux host
- multiple RayJoin-style families exercised
- larger bounded reproduction and performance work completed

### OptiX path

- real GPU bring-up completed
- corrected controlled runtime is in the repo
- bounded correctness ladders completed
- first real-data family validation completed
- larger Goal 41-style GPU checks completed for:
  - `County ⊲⊳ Zipcode`
  - `BlockGroup ⊲⊳ WaterBodies`

### External ground-truth path

- PostGIS is installed on the Linux host
- the project is moving toward indexed PostGIS-based ground-truth comparison for accepted bounded real-data packages
- that PostGIS comparison track is in progress and is not yet a closed v0.1 result

## What Is Still Missing

v0.1 is **not** finished just because both backends exist.

The remaining work is to finish a bounded, trustworthy RayJoin-style repetition
package across the current backends.

That mainly means:

- broader exact-source family coverage
- more apples-to-apples backend comparisons
- finish the PostGIS ground-truth comparison track on accepted bounded packages
- clearer final experiment matrix closure
- final packaging of what is:
  - exact-source and accepted
  - bounded but accepted
  - synthetic only
  - still missing

## Current Acceptance Standard

A v0.1 experiment/result only counts when:

- the goal was explicit
- the result is honestly scoped
- correctness is checked against the oracle where required
- review/consensus artifacts exist
- the repo state is documented cleanly enough to support the next goal

## Immediate Priority

The next v0.1 work should continue from the current clean audited state and aim
at finishing the remaining bounded RayJoin-style experiment matrix across
Embree and OptiX.

That is the right interpretation of “finishing v0.1” from the repo’s current
position.
