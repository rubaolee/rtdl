# Generated OptiX Skeleton

This directory contains generated backend artifacts for the RTDL kernel `county_soil_overlay`.

## Workload

- `overlay`
- predicate: `overlay_compose`
- refine mode: `compose_lsi_plus_pip`

## Contents

- `plan.json`: serialized backend plan.
- `device_kernels.cu`: OptiX device program skeletons.
- `host_launcher.cpp`: host-side launcher skeleton.

## Device Programs

- `__raygen__rtdl_overlay_dispatch`
- `__miss__rtdl_miss`
- `__closesthit__rtdl_overlay_compose`

## Launch Params

- `traversable`: `OptixTraversableHandle` (rt_accel)
- `right_polygons`: `const Polygon2DRef*` (device_input_build)
- `left_polygons`: `const Polygon2DRef*` (device_input_probe)
- `output_records`: `OverlaySeedRecord*` (device_output)
- `output_count`: `uint32_t*` (device_counter)
- `output_capacity`: `uint32_t` (device_limit)
- `probe_count`: `uint32_t` (launch_size)

## Buffers

- `right_polygons`: `Polygon2DRef` (device_input_build)
- `left_polygons`: `Polygon2DRef` (device_input_probe)
- `output_records`: `OverlaySeedRecord` (device_output)
- `output_count`: `uint32_t` (device_counter)
- `output_capacity`: `uint32_t` (device_limit)
