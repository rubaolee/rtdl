# V4.0 Scope Gate

Status: generated V4 Python eDSL/operator-pushdown scope gate

- gate status: `v4_python_edsl_operator_pushdown_scope_goal4742_current_release_framing`
- validation status: `passed`
- release authorized: `False`

## Included Surfaces

- `v4_fixed_radius_count_threshold_2d_device_arrays`
- `v4_closest_hit_grouped_argmin_3d_device_arrays`
- `v4_ray_triangle_any_hit_flags_2d_device_arrays`
- `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
- `v4_point_group_nearest_witness_2d_device_arrays`
- `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`
- `v4_fixed_radius_graph_component_union_3d_device_arrays`
- `v4_aabb_index_query_2d_all_ops_count_prepared_runner`
- `v4_aggregate_frontier_device_columns_2d_prepared_runner`
- `v4_ray_triangle_custom_predicate_early_exit_3d_numba`

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

- `goal4742_all_historical_benchmark_apps_faster_claim_not_supported`

## Non-Authorization

This gate preserves the V4 Python eDSL/operator-pushdown surface, including constrained custom predicate early-exit. It does not authorize broad legacy all-app high-performance wording, broad V4 speedup wording, whole-application speedups, Tier-3 callback/PTX support, raw OptiX callbacks, CuPy performance claims beyond measured rows, embedding/C-ABI, non-Python host binding claims, or app-specific native kernels.
