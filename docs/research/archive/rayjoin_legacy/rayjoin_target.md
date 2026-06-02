# RayJoin Target

RayJoin is the first serious application target for RTDL because it makes the
core project problem concrete.

Full reference:

- Liang Geng, Rubao Lee, and Xiaodong Zhang,
  *RayJoin: Fast and Precise Spatial Join*,
  Proceedings of the 38th ACM International Conference on Supercomputing
  (ICS 2024),
  DOI `10.1145/3650200.3656610`

Why RayJoin matters here:

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
- long exact-source OptiX closure on the accepted `county_zipcode`
  positive-hit `pip` surface
- long exact-source Embree closure on that same surface
- long exact-source Vulkan parity closure on that same surface, without a
  competitive performance claim
- bounded PostGIS-backed four-system closures on accepted packages
- bounded accepted package closure across:
  - `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
  - `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`
  - bounded `LKAU ⊲⊳ PKAU`
  - bounded `LKAU ⊲⊳ PKAU` `overlay-seed analogue`

So RayJoin is no longer only a future target in this repo. It is the active
application slice that drives RTDL v0.1.

Important current boundary:

- the bounded package remains the v0.1 trust anchor
- the strongest performance claim surface is the long exact-source
  `county_zipcode` positive-hit `pip` row

## Why this is still only a first step

RTDL v0.1 does not claim full paper-identical reproduction of every RayJoin
dataset family.

What it does claim is narrower and more useful:

- RayJoin is a real application target for RTDL, not just an idea
- the key workload family can be expressed in the language/runtime
- the strongest backend rows are now parity-clean and performance-credible
- the remaining deferred rows are documented instead of hidden
