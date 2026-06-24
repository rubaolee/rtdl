# V4.0 Scope Gate

Status: generated development gate, not a release authorization

- gate status: `v4_0_development_scope_defined_not_release`
- validation status: `passed`
- release authorized: `False`

## Included Surfaces

- `v4_fixed_radius_count_threshold_2d_device_arrays`
- `v4_closest_hit_grouped_argmin_3d_device_arrays`
- `v4_ray_triangle_any_hit_flags_2d_device_arrays`

## Deferred To V4.x

- `tier3_numba_ptx_optix_callback_support`
- `raw_optix_callback_public_api`
- `cupy_measured_performance_claims`
- `embedding_c_abi`
- `non_python_host_bindings`
- `app_specific_native_engine_kernels`

## Blocking Reasons

- `external_release_review_not_obtained`
- `release_decision_record_not_obtained`
- `tier2_operator_catalog_review_debt_open`

## Non-Authorization

This gate does not authorize V4 release, broad V4 speedup wording, Tier-3 callback/PTX support, raw OptiX callbacks, embedding/C-ABI, or app-specific native kernels.
