# Generated OptiX Skeleton

This directory contains generated backend artifacts for the RTDL kernel `central_ray_triangle_stats`.

## Workload

- `ray_tri_hitcount`
- predicate: `ray_triangle_hit_count`
- refine mode: `analytic_float_ray_triangle_hit_count`

## Contents

- `plan.json`: serialized backend plan.
- `device_kernels.cu`: OptiX device program skeletons.
- `host_launcher.cpp`: host-side launcher skeleton.

## Device Programs

- `__raygen__rtdl_ray_hitcount`
- `__miss__rtdl_miss`
- `__anyhit__rtdl_triangle_count`
- `__intersection__rtdl_triangles`

## Launch Params

- `traversable`: `OptixTraversableHandle` (rt_accel)
- `triangles`: `const Triangle2D*` (device_input_build)
- `rays`: `const Ray2D*` (device_input_probe)
- `output_records`: `RayHitCountRecord*` (device_output)
- `output_count`: `uint32_t*` (device_counter)
- `output_capacity`: `uint32_t` (device_limit)
- `probe_count`: `uint32_t` (launch_size)

## Buffers

- `triangles`: `Triangle2D` (device_input_build)
- `rays`: `Ray2D` (device_input_probe)
- `output_records`: `RayHitCountRecord` (device_output)
- `output_count`: `uint32_t` (device_counter)
- `output_capacity`: `uint32_t` (device_limit)
