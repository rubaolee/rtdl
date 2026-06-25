# V4.0 Scope Gate

Status: generated V4.0.0 formal release scope gate

- gate status: `v4_0_0_formal_release_scope_authorized`
- validation status: `passed`
- release authorized: `True`

## Included Surfaces

- `v4_fixed_radius_count_threshold_2d_device_arrays`
- `v4_closest_hit_grouped_argmin_3d_device_arrays`
- `v4_ray_triangle_any_hit_flags_2d_device_arrays`
- `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
- `v4_point_group_nearest_witness_2d_device_arrays`
- `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`
- `v4_fixed_radius_graph_component_union_3d_device_arrays`
- `v4_aabb_index_query_2d_all_ops_count_prepared_runner`

## Candidate Surfaces

- none

## Deferred To V4.x

- `tier3_numba_ptx_generation_spike_only`
- `tier3_numba_bare_ptx_direct_optix_module_link_blocked`
- `tier3_wrapper_direct_callable_abi`
- `raw_optix_callback_public_api`
- `cupy_measured_performance_claims`
- `embedding_c_abi`
- `non_python_host_bindings`
- `app_specific_native_engine_kernels`

## Blocking Reasons

- none

## Non-Authorization

This gate authorizes the narrow V4.0.0 generic operator release. It does not authorize broad V4 speedup wording, whole-application speedups, Tier-3 callback/PTX support, raw OptiX callbacks, CuPy performance claims, embedding/C-ABI, non-Python host binding claims, or app-specific native kernels.
