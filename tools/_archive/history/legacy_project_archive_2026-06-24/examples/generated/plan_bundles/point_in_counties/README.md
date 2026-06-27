# Generated OptiX Skeleton

This directory contains generated backend artifacts for the RTDL kernel `point_in_counties`.

## Workload

- `pip`
- predicate: `point_in_polygon`
- refine mode: `analytic_float_point_in_polygon`

## Contents

- `plan.json`: serialized backend plan.
- `device_kernels.cu`: OptiX device program skeletons.
- `host_launcher.cpp`: host-side launcher skeleton.

## Device Programs

- `__raygen__rtdl_pip_probe`
- `__miss__rtdl_miss`
- `__closesthit__rtdl_pip_refine`
- `__intersection__rtdl_polygon_refs`

## Launch Params

- `traversable`: `OptixTraversableHandle` (rt_accel)
- `polygons`: `const Polygon2DRef*` (device_input_build)
- `points`: `const Point2D*` (device_input_probe)
- `output_records`: `PointInPolygonRecord*` (device_output)
- `output_count`: `uint32_t*` (device_counter)
- `output_capacity`: `uint32_t` (device_limit)
- `probe_count`: `uint32_t` (launch_size)

## Buffers

- `polygons`: `Polygon2DRef` (device_input_build)
- `points`: `Point2D` (device_input_probe)
- `output_records`: `PointInPolygonRecord` (device_output)
- `output_count`: `uint32_t` (device_counter)
- `output_capacity`: `uint32_t` (device_limit)
