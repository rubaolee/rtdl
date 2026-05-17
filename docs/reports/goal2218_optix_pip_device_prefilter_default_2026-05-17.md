# Goal2218: OptiX PIP Device Prefilter Default

Status: local implementation ready for pod validation.

## Purpose

Goal2217 showed that the device prefilter is the right next step for the RayJoin same-query PIP weak spot. On the pod experiment, it reduced conservative GPU candidates from about `2.8M` to about `8.8K`, preserved CPU-reference parity, and moved RTDL OptiX PIP from about `0.62 s` to about `0.116 s`.

Goal2218 promotes the device prefilter to the default for positive-only PIP.

## Runtime Contract

Default positive-only PIP now:

- uses OptiX traversal to find candidate point/shape intersections;
- runs the inclusive device point-in-polygon helper before emitting compact candidates;
- still runs host exact refinement over all surviving candidates;
- keeps the engine app-agnostic and dataset-free.

The conservative all-AABB mode remains available with:

`RTDL_OPTIX_PIP_DISABLE_DEVICE_PREFILTER=1`

This opt-out exists for diagnosis and for any future precision investigation. It is not the default public path.

## Claim Boundary

This source change does not by itself authorize a public performance claim. The required next step is a pod rerun without `RTDL_OPTIX_PIP_DEVICE_PREFILTER`, proving the default path preserves parity and reproduces the faster timing.
