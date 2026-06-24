# Call For Review: V4 Second Tier-2 Device-Array Primitive

Requested verdict labels:

- `accept_continue_next_v4_primitive`
- `accept_with_required_amendments`
- `reject_not_v4_progress`
- `blocked_insufficient_evidence`

## Context

V4 is being built as a Python GPU-ecosystem RT-core lane: caller-owned GPU
arrays go in, generic RTDL fused primitives run, caller-owned GPU arrays come
out. This review covers the second measured Tier-2 primitive surface:
`CLOSEST_HIT_GROUPED_ARGMIN_3D`.

The first implementation wrote internal native grouped outputs then copied them
to caller tensors. That was rejected as suboptimal and replaced with direct
native writes into caller-owned output columns.

## Files To Review

Implementation:

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/v4_ray_triangle.py`

Validation and tests:

- `scripts/v4_section8_closest_hit_grouped_argmin_device_frontdoor_validation.py`
- `tests/v4_ray_triangle_device_array_api_test.py`
- `tests/v4_section8_closest_hit_grouped_argmin_device_frontdoor_validation_test.py`
- `tests/v4_fixed_radius_docs_and_example_test.py`

Docs/examples/evidence:

- `future/v4/ray_triangle_device_array_frontdoor.md`
- `future/v4/examples/closest_hit_grouped_argmin_torch_device_arrays.py`
- `future/v4/evidence/v4_section8_closest_hit_grouped_argmin_device_frontdoor_result_2026-06-24.json`
- `future/v4/evidence/v4_section8_closest_hit_grouped_argmin_device_frontdoor_report_2026-06-24.md`
- `future/v4/evidence/v4_closest_hit_grouped_argmin_torch_device_arrays_example_result_2026-06-24.json`

## Measured Result

POD validation passed correctness for all rows.

| rays | triangles | groups | direct device-array median | legacy host-materialize median | ratio |
|---:|---:|---:|---:|---:|---:|
| 8,192 | 8,192 | 1,024 | 0.000092s | 0.000142s | 1.542x |
| 32,768 | 32,768 | 4,096 | 0.000102s | 0.000161s | 1.575x |
| 131,072 | 131,072 | 16,384 | 0.000125s | 0.000217s | 1.729x |

Important metadata:

- `native_direct_device_output_columns: true`
- `grouped_result_device_to_device_export: false`
- `grouped_results_downloaded_to_host_in_hot_path: false`
- `host_materialization_in_hot_path: false`
- `python_ray_object_boundary_in_hot_path: false`

## Questions

1. Is this real V4 progress under the three-tier fused architecture, or just
   another wrapper?
2. Does the direct native output path correctly avoid the earlier D2D-copy
   mistake?
3. Are the correctness and timing boundaries honest?
4. Are the claim boundaries strong enough: no V4 release, no broad speedup, no
   Tier-3 callback, no app-specific kernel claim?
5. Is it acceptable to continue to the next V4 primitive after any required
   amendments, or should this surface be held?

## Non-Authorization

This review must not authorize V4 release, broad V4 speedup claims, whole-app
claims, Tier-3 callback/PTX claims, embedding/C ABI release, or replacing the
public V3 front door.
