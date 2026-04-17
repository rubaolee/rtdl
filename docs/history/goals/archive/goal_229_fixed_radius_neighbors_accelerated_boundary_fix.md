# Goal 229: fixed_radius_neighbors Accelerated Boundary Fix

Date: 2026-04-10
Status: implemented

## Goal

Fix the shared accelerated `fixed_radius_neighbors` boundary bug exposed by the
heavy Linux Goal 228 benchmark, where Embree, OptiX, and Vulkan dropped the
same interior neighbors on a large-coordinate Natural Earth case.

## Acceptance

- Embree, OptiX, and Vulkan return the same `fixed_radius_neighbors` rows as
  CPU and indexed PostGIS on the heavy Goal 228 Natural Earth case
- a focused regression test captures the large-coordinate near-boundary pattern
- the fix preserves the public inclusive-radius contract
- Linux reruns verify the heavy-case parity restoration

## Boundary

- This goal fixes the correctness gap; it does not change the public workload
  API.
- It is not a release-tagging step by itself.
