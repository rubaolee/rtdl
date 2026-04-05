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
  - Vulkan as the supported portable GPU backend, parity-clean on the accepted
    long exact-source `county_zipcode` surface, but slower there than OptiX,
    Embree, and PostGIS
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
  - Vulkan on the accepted bounded Goal 65/66 Linux surface

### Embree path

- mature controlled CPU backend
- real-data validation on Linux host
- multiple RayJoin-style families exercised
- larger bounded reproduction and performance work completed
- accepted long exact-source `county_zipcode` positive-hit `pip` prepared and
  repeated raw-input wins against PostGIS now exist

### OptiX path

- real GPU bring-up completed
- corrected controlled runtime is in the repo
- bounded correctness ladders completed
- bounded real-data family validation completed
- larger Goal 41-style GPU checks completed for:
  - `County ⊲⊳ Zipcode`
  - `BlockGroup ⊲⊳ WaterBodies`
- accepted long exact-source `county_zipcode` positive-hit `pip` prepared and
  repeated raw-input wins against PostGIS now exist

### Vulkan path

- hardware-validated backend path exists
- accepted bounded package support exists
- accepted long exact-source `county_zipcode` positive-hit `pip` prepared and
  repeated raw-input parity closure now exists
- Vulkan remains slower than PostGIS, Embree, and OptiX on that surface

### External ground-truth path

- PostGIS is installed on the Linux host
- indexed PostGIS-based ground-truth comparison is now closed for accepted bounded real-data packages
- accepted bounded four-system closures now exist for:
  - `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
  - `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`
  - bounded `LKAU ⊲⊳ PKAU`
- accepted bounded `overlay-seed analogue` closure now exists for bounded
  `LKAU ⊲⊳ PKAU`

### Current bounded package

The strongest currently accepted bounded v0.1 package is:

- `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
- `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`
- bounded `LKAU ⊲⊳ PKAU`
- bounded `LKAU ⊲⊳ PKAU` `overlay-seed analogue`
  - this means seed-generation closure for overlay-style work, not full
    polygon output materialization

Across:

- PostGIS
- native C oracle
- Embree
- OptiX
- Vulkan on the accepted bounded Linux surface

### Strongest current performance surface

The strongest current performance surface is:

- long exact-source `county_zipcode`
- positive-hit `pip`

On that surface:

- OptiX is parity-clean and faster than PostGIS on the accepted repeated
  raw-input boundary, and has an accepted warmed prepared win
- Embree is parity-clean and faster than PostGIS on the accepted prepared and
  repeated raw-input boundaries
- Vulkan is parity-clean on the accepted prepared and repeated raw-input
  boundaries, but slower than PostGIS

## What Is Still Missing Beyond v0.1 Closure

The bounded package is still the main v0.1 trust anchor, but the following work
is still open for later releases or post-v0.1 hardening:

- larger-package Vulkan `lsi` scaling beyond the current output-capacity contract
- lower-overhead Vulkan exact-finalization design
- broader exact-source family coverage beyond the accepted bounded package
- more apples-to-apples large-package backend comparisons
- any paper-identical reproduction that depends on unstable or otherwise
  unavailable datasets

## Current Acceptance Standard

A v0.1 experiment/result only counts when:

- the goal was explicit
- the result is honestly scoped
- correctness is checked against the oracle where required
- review/consensus artifacts exist
- the repo state is documented cleanly enough to support the next goal

## Immediate Priority

The immediate priority is no longer backend-capability proof.

The remaining v0.1 work is:

- release-facing reproduction closure
- release-head validation
- release docs
- final release audit

That means:

- preserve the accepted bounded package as the current trust anchor
- preserve the long exact-source backend closure as the strongest current
  performance surface
- avoid broadening claims beyond stable, already-stageable evidence
