# Goal2212: OptiX PIP Compact Positive-Hit Output

Status: local implementation ready for pod validation.

## Why This Exists

Goal2209 showed that RTDL OptiX PIP was correct but far too slow on the RayJoin-exported same-query stream:

- RTDL Embree PIP: about `0.106 s`
- RTDL OptiX PIP: about `4.108 s`
- RayJoin RT PIP query phase: about `0.575 ms`

The main implementation problem was visible in the native OptiX PIP positive-hit path. It wrote a bitmap over the full point-by-polygon Cartesian space and then scanned that bitmap on the host. For the Goal2209 stream, that means scanning billions of possible slots to recover only `8686` positive rows.

## Fix

`src/native/optix/rtdl_optix_core.cpp` and `src/native/optix/rtdl_optix_workloads.cpp` now use compact positive-hit candidate output for PIP:

- count pass: OptiX any-hit atomically counts conservative positive candidates;
- write pass: OptiX writes only compact candidate records;
- host exact refinement visits only those candidate records;
- the launch is chunked by point count when needed to keep each point-by-polygon chunk inside a 32-bit launch/candidate space.

This remains app-agnostic. The code does not mention RayJoin, maps, counties, ZIPs, or any dataset. It is a generic point/primitive positive-hit output strategy.

## Claim Boundary

This fix does not authorize a speedup claim yet. The required next step is a pod rerun against the same Goal2198/Goal2209 RayJoin query stream contract, with imported evidence and external review.

