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
- indexed PostGIS-based ground-truth comparison is now closed for accepted bounded real-data packages
- accepted bounded four-system closures now exist for:
  - `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
  - `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`
  - bounded `LKAU ⊲⊳ PKAU`
- bounded `overlay-seed analogue` closure now exists for:
  - bounded `LKAU ⊲⊳ PKAU`

### Current bounded package

The strongest currently accepted bounded v0.1 package is:

- `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
- `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`
- bounded `LKAU ⊲⊳ PKAU`
- bounded `LKAU ⊲⊳ PKAU` `overlay-seed analogue`

Across:

- PostGIS
- native C oracle
- Embree
- OptiX

## What Is Still Missing

v0.1 is **not** finished just because both backends exist.

The remaining work is to finish a bounded, trustworthy RayJoin-style repetition
package across the current backends.

That mainly means:

- broader exact-source family coverage
- more apples-to-apples backend comparisons
- expand the bounded PostGIS-backed matrix beyond the currently accepted packages
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

The immediate priority after this bounded package is to extend matrix closure
only on stable, already-stageable workload families and to avoid spending v0.1
time on externally unstable acquisition paths.

That means:

- preserve the accepted bounded package as the current trust anchor
- expand only when data staging is stable and repeatable
- keep Vulkan explicitly provisional until it has materially stronger
  validation evidence
