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
- support a RayJoin-oriented experiment/reporting workflow

## What RTDL Cannot Yet Claim

RTDL does not yet claim:

- exact computational geometry
- a finished generalized multi-backend optimizer
- full paper-scale reproduction for every RayJoin family
- broad CI-backed cross-platform enforcement

## Runtime Surface

Current execution paths:

- `rt.run_cpu(...)`: native oracle
- `rt.run_embree(...)`: controlled CPU backend
- `rt.run_optix(...)`: controlled GPU backend

Current practical interpretation:

- oracle for ground truth
- Embree for mature CPU execution
- OptiX for validated but still earlier-stage GPU execution

## Recommended Reading

If you need:

- exact language contract:
  [DSL Reference](rtdl/dsl_reference.md)
- authoring guidance:
  [Programming Guide](rtdl/programming_guide.md)
- copyable examples:
  [Workload Cookbook](rtdl/workload_cookbook.md)
- whole-project framing:
  [Vision](vision.md)

## Bottom Line

RTDL is already a real multi-backend research system, but still a bounded one.

The right way to read the current repo is:

- live, executable, and validated on its accepted workloads
- still narrow and correctness-conscious
- still expanding toward a fuller bounded RayJoin-style reproduction package
