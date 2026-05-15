# Generated OptiX Skeleton

This directory contains generated backend artifacts for the RTDL kernel `county_zip_join`.

## Workload

- `lsi`
- predicate: `segment_intersection`
- refine mode: `analytic_float_segment_intersection`

## Contents

- `plan.json`: serialized backend plan.
- `device_kernels.cu`: OptiX device program skeletons.
- `host_launcher.cpp`: host-side launcher skeleton.

## Device Programs

- `__raygen__rtdl_probe`
- `__miss__rtdl_miss`
- `__closesthit__rtdl_refine`
- `__intersection__rtdl_segments`

## Launch Params

- `traversable`: `OptixTraversableHandle` (rt_accel)
- `right_segments`: `const Segment2D*` (device_input_build)
- `left_segments`: `const Segment2D*` (device_input_probe)
- `output_records`: `IntersectionRecord*` (device_output)
- `output_count`: `uint32_t*` (device_counter)
- `output_capacity`: `uint32_t` (device_limit)
- `probe_count`: `uint32_t` (launch_size)

## Buffers

- `right_segments`: `Segment2D` (device_input_build)
- `left_segments`: `Segment2D` (device_input_probe)
- `output_records`: `IntersectionRecord` (device_output)
- `output_count`: `uint32_t` (device_counter)
- `output_capacity`: `uint32_t` (device_limit)
