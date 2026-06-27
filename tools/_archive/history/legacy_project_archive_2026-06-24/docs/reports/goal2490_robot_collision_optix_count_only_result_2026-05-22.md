# Goal2490: OptiX Count-Only Prepared Grouped Segment Result

Date: 2026-05-22

## Status

Goal2490 is complete with local validation and pod OptiX validation. It follows
Goal2489 by adding a count-only result mode for the same generic OptiX prepared
grouped 3D segment query path. The purpose is feasibility screening: when the
caller only needs the number of flagged query groups, Python should not have to
materialize every compact group flag as a list.

## What Changed

- Added `rtdl_optix_static_triangle_scene_3d_grouped_segment_query_any_hit_count`.
- Added `PreparedOptixStaticTriangleScene3D.run_native_prepared_grouped_segment_any_hit_count`.
- Added robot benchmark mode `optix_prepared_device_count`.
- The mode reuses the same native OptiX prepared scene and prepared grouped
  segment query buffers introduced in Goal2489.
- The result returned to Python is a scalar `uint32` flagged-group count.

## Boundary

This is not true zero-copy. Native OptiX still writes compact group flags on the
device, then native host code downloads those flags and counts them. The new
boundary avoids Python group-flag list materialization and returns only a scalar
count to Python.

This adds no robot-specific native ABI. The native engine remains expressed in
generic terms: static triangle scene, grouped finite 3D segment query, any-hit
flags, and flagged group count. Robot/link/pose/collision semantics remain in
the Python benchmark layer.

## Claim Policy

The public speedup claim is not authorized by this document. The implementation
and pod data are internal exact-subpath evidence for a count-only result
contract. External review is required before any public wording.

## Expected Effect

For screening-style callers, the expected effect is to remove Python list
materialization for group flags. It does not remove the native host download of
group flags. It also does not alter RT traversal semantics. A future stronger
version could replace the native host count with a true device-side reduction
behind the same count-only API.

## Validation Plan

- Local syntax and regression test:
  `PYTHONPATH=src:. python3 -m unittest tests.goal2490_robot_collision_optix_count_only_result_test`
- Native vocabulary guard over active OptiX native files.
- Pod OptiX build with CUDA 13.
- Pod comparison between `optix_prepared_device_buffers` and
  `optix_prepared_device_count` on the same scaled case.

## Pod Evidence

Pod command: `ssh root@157.157.221.29 -p 23792 -i ~/.ssh/id_ed25519_rtdl_codex`

Environment:

- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 570.133.07
- Build/run CUDA: 13.0 (`/usr/local/cuda`)
- OptiX headers: `/workspace/vendor/optix-dev`

Scaled benchmark shape:

- Dataset: `scaled`
- Poses: 64
- Links: 3
- Static obstacle triangles: 32
- Groups: 192
- Segments: 1728
- Protocol: 11 repeats, first 3 warmup rows dropped
- Reference flagged-group count: 70

Results:

| Mode | Tail Median Total (s) | Tail Median Traversal (s) | Tail Median Output Postprocess (s) | Python Group Flags Materialized |
| --- | ---: | ---: | ---: | --- |
| `optix_prepared_device_buffers` | 0.0001154877245426178 | 0.000040051 | 0.00003897026181221008 | yes |
| `optix_prepared_device_count` | 0.000050187110900878906 | 0.0000298915 | 0.0000003129243850708008 | no |

Internal exact-subpath ratio:

- Repeated-run total median: `optix_prepared_device_buffers / optix_prepared_device_count = 2.3011431116389547x`
- Output-postprocess median: `optix_prepared_device_buffers / optix_prepared_device_count = 124.53571428571429x`

Interpretation: for count-only screening, the measured gain comes from avoiding
Python per-group flag list materialization and returning only a scalar count.
The implementation still downloads compact group flags inside native host code,
so this result does not authorize true zero-copy wording.

## Artifacts

- `docs/reports/goal2490_robot_collision_optix_count_only_result_pod/`
