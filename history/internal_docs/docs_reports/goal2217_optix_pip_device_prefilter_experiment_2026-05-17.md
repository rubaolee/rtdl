# Goal2217: OptiX PIP Device Prefilter Experiment

Status: local opt-in implementation ready for pod validation.

## Purpose

Goal2216 telemetry showed that RTDL OptiX PIP traversal is no longer the bottleneck on the RayJoin same-query stream. The expensive phase is host exact refinement over about `2.8M` conservative AABB candidates, which then emits only `8686` final rows.

Goal2217 adds an opt-in device-side prefilter controlled by `RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DEVICE_PREFILTER`.

## Design

Default behavior remains conservative:

- OptiX reports every point/polygon AABB candidate;
- host exact refinement decides final inclusive truth.

When `RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DEVICE_PREFILTER` is set:

- the OptiX intersection program runs the existing inclusive point-in-polygon helper before reporting a positive-only candidate;
- obvious non-hits are removed on device;
- the host exact-refine step still runs over every surviving compact candidate;
- correctness is still checked against CPU reference rows in pod validation before any performance interpretation.

This remains app-agnostic. The prefilter is a generic point/shape candidate filter and contains no RayJoin-specific dataset, query, or paper logic.

## Claim Boundary

This is an experiment until pod evidence proves parity. It does not authorize making the prefilter the default, a RayJoin speedup claim, a broad RT-core speedup claim, or v2.0 release readiness.
