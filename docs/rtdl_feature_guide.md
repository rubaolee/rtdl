# RTDL Feature Guide

This is the **high-level orientation guide** for RTDL.

Audience:

- readers who want a fast overview of what RTDL currently is
- people deciding whether the current system fits their use case
- reviewers who need the feature surface without reading the full language docs

This guide is intentionally lighter than the documents in `docs/rtdl/`.

## What RTDL Is Today

RTDL is a Python-hosted DSL for non-graphical ray-tracing-style workloads.

Today it includes:

- a kernel authoring surface
- compiler IR and lowering
- a native C/C++ oracle
- a controlled Embree backend
- a controlled OptiX backend
- a Vulkan backend that is now hardware-validated and parity-clean on the
  accepted long exact-source `county_zipcode` positive-hit `pip` surface, but
  slower than PostGIS, OptiX, and Embree there

Current supported workload families:

- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`
- `segment_polygon_hitcount`
- `point_nearest_segment`

## What RTDL Can Currently Do

The current repo can:

- author kernels in a constrained Python DSL
- compile and lower them
- run them through the native oracle
- run them on Embree
- run accepted long exact-source `county_zipcode` positive-hit `pip` workloads
  on OptiX and Embree with exact parity and accepted performance wins against
  PostGIS on the prepared/repeated boundaries
- run the accepted long exact-source Vulkan surface with exact parity, while
  keeping Vulkan as the slower portable backend
- compare accepted workloads against indexed PostGIS ground-truth queries on the Linux host
- close bounded four-system checks across PostGIS, native oracle, Embree, and OptiX on accepted packages
- support a RayJoin-oriented experiment/reporting workflow
- preserve a bounded accepted v0.1 reproduction package as the current trust anchor

## What RTDL Cannot Yet Claim

RTDL does not yet claim:

- exact computational geometry
- a finished generalized multi-backend optimizer
- full paper-identical reproduction of every RayJoin dataset family
- high-precision native GPU geometry on Vulkan (the accepted bounded path still
  relies on float32 traversal plus exact host-side final truth)
- that every backend/workload/boundary combination is equally mature
- full polygon overlay materialization (`overlay` is still a seed analogue)
