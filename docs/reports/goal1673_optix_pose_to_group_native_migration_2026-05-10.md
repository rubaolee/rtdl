# Goal1673 OptiX Pose-To-Group Native Migration

Date: 2026-05-10

Status: first local migration from app-shaped native terminology to generic
primitive terminology.

## Verdict

The OptiX 2-D prepared any-hit grouped-summary path no longer exports
pose-shaped native symbols. The native ABI now describes the operation as
generic group indices and group flags:

- `rtdl_optix_group_flags_prepared_ray_anyhit_2d_packed`
- `rtdl_optix_prepare_group_indices_2d`
- `rtdl_optix_group_flags_prepared_ray_anyhit_2d_prepared_indices`
- `rtdl_optix_count_groups_prepared_ray_anyhit_2d_prepared_indices`
- `rtdl_optix_destroy_prepared_group_indices_2d`

This is a local source migration only. It does not claim new OptiX performance
evidence, because no pod was used.

## Boundary

The Python layer keeps compatibility aliases for existing callers:

- `OptixPoseIndexBuffer` aliases `OptixGroupIndexBuffer`.
- `prepare_optix_pose_indices_2d()` forwards to
  `prepare_optix_group_indices_2d()`.
- `pose_flags_*` and `pose_count_*` prepared-scene methods forward to the new
  `group_flags_*` and `group_count_*` methods.

Those aliases are Python compatibility surface, not native engine terminology.
The generic Python primitive path now calls the group-named methods directly.

## App-Agnostic Impact

Goal1672 classified the old pose-shaped native symbols under
`ray_packet_preparation`. This migration removes that family from the OptiX
native release surface by renaming it to generic grouped primitive language.

The broader app-agnostic gate still fails. Database, graph, polygon/GIS, KNN,
Hausdorff, Jaccard, and other app-shaped native symbols remain and still block
any full native app-agnostic claim.

## Validation

Local validation:

```text
py -3 -m unittest tests.goal671_optix_prepared_anyhit_count_test tests.goal1306_v1_5_robot_pose_flags_generic_migration_test
py -3 -m unittest tests.goal1668_native_engine_app_agnostic_directive_test tests.goal1672_native_app_leakage_migration_classification_test
py -3 -m py_compile src/rtdsl/optix_runtime.py src/rtdsl/generic_primitives.py src/rtdsl/__init__.py
```

Current source audit:

- `src/native/optix/rtdl_optix_api.cpp`: no `pose` term remains.
- `src/native/optix/rtdl_optix_prelude.h`: no `pose` term remains.
- `src/native/optix/rtdl_optix_workloads.cpp`: no `pose` term remains.

No pod validation was run. Native rebuild/runtime validation on an OptiX host is
the next evidence step before treating this as hardware-proven.
