# Goal3765 HIPRT Prepared Grouped Any-Hit Flags

Date: 2026-06-07

## Purpose

Goal3765 removes the most obvious HIPRT robot-collision route gap after
Goal3764. The old HIPRT app path could run Ray2D/Triangle2D any-hit rows, but
the app still had to materialize per-ray rows and reduce them into pose/group
flags in Python. Goal3765 adds the same app-free contract shape already used by
OptiX: prepared ray/triangle any-hit plus generic grouped visibility flags.

The new native symbol is:

`rtdl_hiprt_group_flags_prepared_ray_anyhit_2d_packed`

It uses generic rays, generic group indices, and generic group flags. It does
not contain robot, pose, or app-specific native logic.

## Implementation

- Added a HIPRT grouped any-hit kernel `RtdlGroupedRayAnyhit2DKernel`.
- The kernel uses `atomicExch(&group_flags[group], 1u)` because many rays can
  map to the same group.
- Added lazy query-kernel compilation to `PreparedRayAnyhit2D`: row and grouped
  kernels compile only when the corresponding query path is used.
- Added `HiprtRay2DBuffer` and `prepare_hiprt_rays_2d` so the generic prepared
  primitive can call HIPRT through the same prepared-scene/prepared-rays shape.
- Expanded `run_generic_prepared_ray_triangle_any_hit_grouped_count_threshold_bool`
  to accept `backend="hiprt"` for grouped summaries, while keeping prepared
  scalar count unavailable for HIPRT unless a real count method exists.
- Extended the robot-collision app's `prepared_pose_flags` mode to work with
  `backend="hiprt"` as `hiprt_prepared_pose_flags`.
- Fixed a count-field bug in the prepared pose-flags helper: `colliding_pose_count`
  now counts only true flags.
- Added `prepared_grouped_visibility_flags_2d` to the engine feature matrix.

## A5000 Evidence

Artifact:

`docs/reports/goal3765_robot_collision_hiprt_prepared_group_flags_a5000.json`

Environment:

- GPU: NVIDIA RTX A5000, driver 580.126.09
- Source commit: `cfbf0d88`
- Scoped source dirty: `false`
- HIPRT SDK: `/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`

Validation:

- `make build-hiprt` passed from a fresh clone.
- `tests.goal3765_hiprt_prepared_grouped_anyhit_flags_test`
- `tests.goal674_hiprt_prepared_anyhit_2d_test`
- `tests.goal3764_robot_collision_hiprt_cuda_path_app_smoke_test`
- 14 tests passed on the pod.

Correctness:

- 2 correctness cases.
- Row route and prepared grouped-flag route both matched the CPU oracle.
- Prepared grouped flags matched the row route's pose flags.

## Timing

Same app-level pose-flag output contract, HIPRT row route versus HIPRT prepared
grouped flags:

| Pose count | Row route median sec | Prepared grouped flags median sec | Prepared/row ratio |
| ---: | ---: | ---: | ---: |
| 64 | 0.680315 | 0.587802 | 1.157x |
| 128 | 0.617379 | 0.648363 | 0.952x |
| 256 | 0.735773 | 0.703279 | 1.046x |
| 512 | 0.631174 | 0.602394 | 1.048x |
| 1024 | 0.625932 | 0.734180 | 0.853x |

Interpretation:

The generic grouped-summary route is now functional and sometimes faster, but
the timing is mixed at this scale. The main engineering win is contract closure:
HIPRT can now return compact grouped visibility flags without Python row
materialization. The next performance step is not another app-specific path; it
is a stronger HIPRT prepared/resident query model that separates scene setup,
query-kernel compilation, ray packing, and repeated query timing more cleanly.

## AMD Boundary

This is NVIDIA CUDA/Orochi HIPRT evidence, not AMD hardware evidence. It does
not authorize release claims, AMD hardware performance claims, HIPRT release
claims, broad RT-core claims, whole-app speedup claims, or RTDL-beats-paper
claims. The AMD lane still needs a real AMD HIPRT pod run.

This report does not authorize any release or public performance claim.

## Follow-Up

1. Run the robot-collision HIPRT row and prepared grouped-flag routes on AMD
   hardware.
2. Add a HIPRT prepared/reused ray-buffer path if AMD evidence shows host ray
   packing dominates repeated queries.
3. Promote the next HIPRT generic contracts in the parity plan: RayJoin prepared
   segment-pair count and shape-pair active count, then RT-DBSCAN/RTNN grouped
   fixed-radius stream summaries.
