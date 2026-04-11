# Goal 229 Report: fixed_radius_neighbors Accelerated Boundary Fix

Date: 2026-04-10
Status: implemented

## Summary

Goal 228 exposed a real shared accelerated correctness bug in
`fixed_radius_neighbors` on the heavy Natural Earth benchmark case:

- CPU and indexed PostGIS returned `45632` rows
- Embree, OptiX, and Vulkan returned `45626` rows

The missing accelerated rows were all large-coordinate pairs whose exact
double-precision distance was slightly inside the `0.5` radius, but whose
float-path reconstruction moved slightly outside the boundary.

This goal repairs that mismatch without weakening the public contract:

- Embree widens candidate collection at the float query boundary, but still
  performs exact inclusive-radius acceptance in the callback
- OptiX and Vulkan widen candidate collection and then refilter candidates on
  the host using the original double-precision point coordinates before
  returning public rows

## Files Updated

- `/Users/rl2025/rtdl_python_only/src/native/embree/rtdl_embree_api.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_workloads.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/vulkan/rtdl_vulkan_core.cpp`
- `/Users/rl2025/rtdl_python_only/tests/goal200_fixed_radius_neighbors_embree_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal216_fixed_radius_neighbors_optix_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal218_fixed_radius_neighbors_vulkan_test.py`

## Root Cause

The bug was not a public `distance < radius` policy error. The public contract
was already inclusive.

The actual problem was candidate loss caused by float-path query/geometry
representation on large coordinates. For a representative missing pair:

- exact double distance: about `0.499994728462`
- float32 reconstructed distance: about `0.500045059081`

That is enough to lose the pair during accelerated candidate collection even
though the true double-precision pair is inside the radius.

## Implementation

Embree:

- widens `RTCPointQuery.radius` by a small candidate epsilon
- preserves exact final `distance <= radius` filtering in the callback

OptiX and Vulkan:

- widen candidate collection slightly
- allow extra candidate slots during collection
- refilter candidates on the host against original double-precision query and
  search points
- sort and trim back to the public `k_max` contract after exact filtering

## Verification

Local focused regression:

- `PYTHONPATH=src:. python3 -m unittest tests.goal200_fixed_radius_neighbors_embree_test tests.goal216_fixed_radius_neighbors_optix_test tests.goal218_fixed_radius_neighbors_vulkan_test`
  - `Ran 24 tests`
  - `OK (skipped=18)`

Linux backend rerun:

- `PYTHONPATH=src:. python3 -m unittest tests.goal200_fixed_radius_neighbors_embree_test tests.goal216_fixed_radius_neighbors_optix_test tests.goal218_fixed_radius_neighbors_vulkan_test`
  - `Ran 24 tests`
  - `OK`

Linux heavy-case parity rerun:

- CPU: `45632`
- Embree: `45632`
- OptiX: `45632`
- Vulkan: `45632`
- indexed PostGIS: `45632`

## Outcome

The shared accelerated `fixed_radius_neighbors` correctness blocker from Goal
228 is resolved.

This restores honest heavy-case parity for:

- CPU
- Embree
- OptiX
- Vulkan
- indexed PostGIS comparison

The remaining performance findings from Goal 228 still stand:

- GPU is the strongest direction for `knn_rows`
- Embree `knn_rows` remains correct but comparatively weak
- GPU `knn_rows` still has expected float-vs-double epsilon differences in
  distance values even when row identity matches
