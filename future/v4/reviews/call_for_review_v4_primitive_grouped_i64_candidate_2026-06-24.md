# Call For Review: V4 Primitive Grouped-I64 Device-Output Candidate

Date: 2026-06-24
Requested verdict label: one of

- `accept_candidate_continue_to_catalog_promotion_decision`
- `accept_with_required_amendments_before_catalog_decision`
- `reject_candidate_wrong_v4_boundary`
- `blocked_insufficient_evidence`

## Context

V4 is the Python GPU-array RT-core lane. The current measured V4 catalog has
three Torch CUDA Tier-2 surfaces. This change promotes one V2/V2.x generic
primitive into a V4 candidate surface, but does not add it to the measured V4.0
release catalog.

New candidate surface:

`v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`

Source primitive:

`RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D`

## Files To Review

- `src/rtdsl/v4_ray_triangle.py`
- `src/rtdsl/v4.py`
- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/optix_runtime.py`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `scripts/v4_primitive_grouped_i64_device_outputs_validation.py`
- `future/v4/examples/primitive_grouped_i64_reduction_torch_device_arrays.py`
- `future/v4/v2_primitives_to_v4_tier2_inventory_2026-06-24.md`
- `future/v4/tier2_operator_catalog.md`
- `future/v4/ray_triangle_device_array_frontdoor.md`
- `future/v4/README.md`

Evidence:

- `future/v4/evidence/v4_primitive_grouped_i64_device_outputs_lx1_local_gate_2026-06-24.md`
- `future/v4/evidence/v4_primitive_grouped_i64_device_outputs_lx1_local_gate_8192_32768_2026-06-24.json`
- `future/v4/evidence/v4_primitive_grouped_i64_torch_device_arrays_example_result_2026-06-24.json`
- `future/v4/evidence/v4_primitive_grouped_i64_device_outputs_pod_gate_32768_131072_2026-06-24.md`
- `future/v4/evidence/v4_primitive_grouped_i64_device_outputs_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_primitive_grouped_i64_torch_device_arrays_example_result_pod_2026-06-24.json`

## What Changed

1. Added a native direct-device-output symbol for prepared static triangle scene
   + prepared ray batch + prepared primitive grouped i64 payload.
2. Added Python `optix_runtime` handoff validation for caller-owned Torch CUDA
   output columns:
   - `group_counts`
   - `group_sums`
   - `group_mins`
   - `group_maxs`
3. Added V4 candidate API:
   `prepare_primitive_grouped_i64_reduction_3d_device_arrays_v4`.
4. Added catalog/planner candidate visibility, intentionally separate from the
   measured V4 release catalog.
5. Added a repeatable validation script and user-facing candidate example.

## Local Results

Local Linux host `lx1`, GTX 1070:

- `make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev CUDA_PREFIX=/usr`
  passed.
- `nm -D build/librtdl_optix.so` shows
  `rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction_device_outputs`.
- Local validation gate passed for 8,192 and 32,768 rays/triangles.

Summary:

| Rays / triangles | Groups | Parity | Direct device-output median | Legacy host-output median | Local ratio |
| --- | ---: | --- | ---: | ---: | ---: |
| 8,192 | 512 | pass for `sum_count`, `min`, `max` | 0.000130703s | 0.000357760s | 2.737x |
| 32,768 | 2,048 | pass for `sum_count`, `min`, `max` | 0.000196054s | 0.001056885s | 5.391x |

These are local GTX results. They do not authorize RT-core performance wording.

## POD Results

RTX A5000 POD:

- `make build-optix OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0 CUDA_PREFIX=/usr/local/cuda-12.8`
  passed.
- The same native symbol was exported and used.
- POD validation gate passed for 32,768 and 131,072 rays/triangles.

Summary:

| Rays / triangles | Groups | Parity | Direct device-output median | Legacy host-output median | Same-contract ratio |
| --- | ---: | --- | ---: | ---: | ---: |
| 32,768 | 2,048 | pass for `sum_count`, `min`, `max` | 0.000168864s | 0.001339529s | 7.933x |
| 131,072 | 8,192 | pass for `sum_count`, `min`, `max` | 0.000212841s | 0.004864600s | 22.856x |

The ratio is `legacy_host_output / direct_device_output` for the same prepared
native primitive. It measures removal of grouped-row host materialization for
this candidate front door. It does not authorize broad V4 speedup wording,
whole-application speedup wording, or release promotion.

## Questions For Reviewer

1. Is this truly a V4 Tier-2 generic operator candidate, not an app-specific
   kernel?
2. Is it correct to keep it outside the measured V4.0 release catalog until
   review and release decision, even though POD evidence now exists?
3. Are the claim boundaries strong enough, especially around:
   - no broad speedup claim
   - no whole-app claim
   - no true-zero-copy claim
   - no Tier-3 callback claim
   - payload prepared once, not direct per-run caller device payload
4. Is the POD gate sufficient to continue to a catalog-promotion decision packet?
5. What must be amended before any catalog promotion?

## Non-Authorization

This packet does not authorize:

- V4 release
- adding this candidate to the measured V4.0 catalog
- broad V4 speedup wording
- whole-application speedup wording
- RT-core POD performance wording
- true-zero-copy public wording
- Tier-3 callback/PTX support
- CuPy performance claims
- embedding/C-ABI or non-Python host claims
- app-specific native engine kernels
