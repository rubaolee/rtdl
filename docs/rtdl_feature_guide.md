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
- a provisional cross-vendor Vulkan KHR backend

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
- run bounded validated workloads on OptiX
- keep a provisional Vulkan KHR backend in the repo for continued validation
- compare accepted workloads against indexed PostGIS ground-truth queries on the Linux host
- close bounded four-system checks across PostGIS, native oracle, Embree, and OptiX on accepted packages
- support a RayJoin-oriented experiment/reporting workflow

## What RTDL Cannot Yet Claim

RTDL does not yet claim:

- exact computational geometry
- a finished generalized multi-backend optimizer
- paper-scale reproduction on GPU backends
- high-precision support on Vulkan (currently float32)
- that PostGIS closure already exists for all intended packages
- full polygon overlay materialization (`overlay` is still a seed analogue)
