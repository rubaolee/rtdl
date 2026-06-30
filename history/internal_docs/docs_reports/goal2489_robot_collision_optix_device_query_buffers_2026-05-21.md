# Goal2489: OptiX Device-Resident Grouped Segment Query Buffers

Date: 2026-05-21

## Status

Goal2489 is the next robot-collision benchmark optimization slice after Goal2488. The implementation moves the grouped 3D segment query from Python-owned reusable host buffers to a native OptiX prepared query handle with device-resident grouped 3D segment query buffers.

## What Changed

- Added a generic native OptiX prepared query handle for `PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1`.
- The handle stores packed segment rays, group offsets, per-segment group indices, and compact group flags on the CUDA device.
- Added a generic OptiX group-flag any-hit continuation that writes compact per-group flags on device and does not materialize per-segment hit records for this mode.
- Added Python runtime support through `PreparedOptixGroupedSegmentQuery3D` and `prepare_optix_grouped_segment_query_3d`.
- Added robot benchmark mode `optix_prepared_device_buffers` to exercise the generic primitive without adding app-specific native vocabulary.

## Boundary

This is not true zero-copy. The Python API still downloads compact group flags to host. The change removes per-run query segment upload and per-segment hit-record download for this prepared-query mode, but it still uploads a small OptiX launch-parameter block each run and returns host-visible flags.

This touches the native OptiX engine, but only by adding a generic RT primitive. It does not add robot, link, pose, collision, or planner semantics to the native OptiX engine. The native ABI remains expressed as a static triangle scene plus grouped finite 3D segment any-hit flags.

## Claim Policy

The public speedup claim is not authorized by this document. Local tests verify API wiring, app-agnostic native vocabulary, metadata boundaries, and benchmark-mode exposure. Pod evidence below supports only an internal exact-subpath conclusion for the prepared grouped segment query path; external review is still required before any public wording.

## Expected Performance Effect

The expected internal effect is lower repeated-run overhead for OptiX workloads where the same segment query is replayed against a prepared static scene. Compared with Goal2488 `optix_prepared_buffers`, this mode should avoid repeated native device allocation/upload for query segments and avoid downloading per-segment any-hit records just to reduce them on the CPU.

The remaining costs are OptiX launch overhead, launch-parameter upload, on-device group flag writes, compact group flag download, and Python list materialization for the current benchmark output.

## Pod Evidence

Pod command: `ssh root@157.157.221.29 -p 23792 -i ~/.ssh/id_ed25519_rtdl_codex`

Environment:

- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 570.133.07
- Build/run CUDA: 13.0 (`/usr/local/cuda`)
- OptiX headers: `/workspace/vendor/optix-dev`
- The first implementation attempt used a standalone CUDA reduction module and exposed a CUDA 13 PTX/driver mismatch on this pod. The final implementation uses an OptiX group-flag any-hit continuation instead, so no standalone CUDA reduction module is required for this path.

Scaled benchmark shape:

- Dataset: `scaled`
- Poses: 64
- Links: 3
- Static obstacle triangles: 32
- Groups: 192
- Segments: 1728
- Protocol: 11 repeats, first 3 warmup rows dropped

Results:

| Mode | Tail Median Total (s) | Tail Median Traversal (s) | Native Device Query/Output Buffers Reused | Query Segments Uploaded Each Run | Per-Segment Records Downloaded |
| --- | ---: | ---: | --- | --- | --- |
| `optix_prepared_buffers` | 0.00012201070785522461 | 0.0000344105 | no | yes | yes |
| `optix_prepared_device_buffers` | 0.00007463246583938599 | 0.000030978499999999995 | yes | no | no |

Internal exact-subpath ratio:

- Repeated-run total median: `optix_prepared_buffers / optix_prepared_device_buffers = 1.6348208046321253x`
- Traversal median: `optix_prepared_buffers / optix_prepared_device_buffers = 1.1107865132269157x`

Interpretation: the optimization improves repeated-run wall-clock overhead for this exact prepared-query path. It does not materially change RT traversal time. The measured gain comes from moving query/output buffers and group reduction into the native device-resident prepared query path.

Artifacts:

- `docs/reports/goal2489_robot_collision_optix_device_query_buffers_pod/summary.json`
- `docs/reports/goal2489_robot_collision_optix_device_query_buffers_pod/optix_prepared_buffers_scaled.json`
- `docs/reports/goal2489_robot_collision_optix_device_query_buffers_pod/optix_prepared_device_buffers_scaled.json`
