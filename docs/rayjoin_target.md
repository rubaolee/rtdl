# RayJoin Target

RayJoin is the first serious application target for RTDL because it shows the
core project problem clearly:

- the workload is not graphics
- the implementation maps well to RT traversal and candidate generation
- the original implementation burden is still backend-heavy and low-level

## Why It Fits RTDL

RayJoin-style workloads require users to reason about:

- data roles
- traversal/candidate generation
- geometric refine semantics
- backend-specific launch/runtime structure

Those are exactly the layers RTDL is meant to separate.

## What RTDL Should Abstract

Users should not need to directly author:

- OptiX program groups
- payload packing
- BVH build plumbing
- SBT setup
- module/pipeline launch mechanics
- backend-specific runtime glue

Those should remain backend/compiler responsibilities.

## What RTDL Should Keep Visible

The source language should still make these explicit:

- workload family
- geometry roles
- output schema
- precision boundary
- execution-mode consequences

## Current RayJoin State In This Repo

Current validated RayJoin-style work includes:

- substantial Embree-side exact-source and bounded reproduction work
- native-oracle-backed correctness checks
- first real-data OptiX validation on bounded RayJoin-family workloads
- bounded PostGIS-backed four-system closures on accepted packages
- bounded accepted package closure across:
  - `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
  - `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`
  - bounded `LKAU ⊲⊳ PKAU`
  - bounded `LKAU ⊲⊳ PKAU` `overlay-seed analogue`

So RayJoin is no longer only a future target in this repo. It is the active
application slice that drives the current v0.1 validation work.
