# Goal 169: Parallel Vulkan / OptiX Backend Closure

## Objective

Close two bounded `v0.3` backend goals in parallel for the orbiting-star 3D demo line:

1. Linux Vulkan orbit-demo rendering closure
2. Linux OptiX 4K-oriented orbit-demo closure

This goal is backend closure for the RTDL geometric-query core.  It is not a
claim that RTDL has become a general rendering engine.

## Accepted Scope

- keep RTDL as the geometric-query core
- keep Python responsible for scene setup, shading, and output
- prove bounded Linux one-frame parity against `cpu_python_reference`
- add focused backend-facing tests and wrapper entry points
- preserve honesty that the ongoing Windows Embree 4K movie line is separate

## Out of Scope

- replacing the Windows Embree movie as the premier public artifact
- claiming Vulkan or OptiX are now the canonical public demo path
- broad renderer-style feature growth
- full 4K Linux production movie closure in this goal
