# V4 Section 8 Closest-Hit Grouped-Argmin Device-Array Front Door

Status: measured V4 development evidence, not a release authorization

This run validates the second V4 Tier-2 device-array surface:
`CLOSEST_HIT_GROUPED_ARGMIN_3D` over caller-owned Torch CUDA triangle, ray,
group, and output columns.

The important change is the output boundary. The first implementation wrote
native internal grouped outputs and then copied them to caller tensors. That
was corrected before the serious run: the measured route now calls
`rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin_device_outputs`,
so native traversal and grouped argmin write directly into caller-owned CUDA
output columns.

## Evidence Summary

Source JSON:
`future/v4/evidence/v4_section8_closest_hit_grouped_argmin_device_frontdoor_result_2026-06-24.json`

Hardware:
RTX POD, same V4 Section 8 worktree and `librtdl_optix.so` build.

| rays | triangles | groups | direct device-array median | legacy host-materialize median | ratio |
|---:|---:|---:|---:|---:|---:|
| 8,192 | 8,192 | 1,024 | 0.000092s | 0.000142s | 1.542x |
| 32,768 | 32,768 | 4,096 | 0.000102s | 0.000161s | 1.575x |
| 131,072 | 131,072 | 16,384 | 0.000125s | 0.000217s | 1.729x |

All three rows passed correctness:

- `group_has_value` matched expected values.
- `group_index` matched expected per-group argmin indices.
- `group_value` matched expected per-group argmin values.

## Boundary

Timed window includes:

- prepared native closest-hit traversal;
- native grouped argmin continuation;
- direct writes into caller-owned Torch CUDA output columns;
- CUDA synchronization.

Timed window excludes:

- fixture construction;
- prepared scene/ray/grouped-input setup;
- host correctness reads after the run.

The comparison baseline is the existing prepared native route followed by
host materialization of grouped results. This validates the V4 device-array
front door and output boundary. It does not claim broad V4 speedup, whole-app
speedup, or release readiness.

## Contract Markers

The measured metadata records:

- `native_direct_device_output_columns: true`
- `grouped_result_device_to_device_export: false`
- `grouped_results_downloaded_to_host_in_hot_path: false`
- `host_materialization_in_hot_path: false`
- `python_ray_object_boundary_in_hot_path: false`
- `release_claim_authorized: false`
- `broad_v4_speedup_claim_authorized: false`
- `tier3_callback_claim_authorized: false`

## Result

This is real V4 progress: a second generic Tier-2 RT primitive now accepts
caller-owned GPU arrays and returns caller-owned GPU arrays, without Python row
objects or hot-path host materialization.
