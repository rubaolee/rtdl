# V4 Operator Catalog

This is the current V4.0.0 catalog. These measured operators and workflows are
generic RT-shaped surfaces. Apps compose these operators; they do not call
app-identity kernels.

Most measured operators sit around 1.2x-1.7x against their stated brute-force partner/CPU baselines. Larger rows are scale-dependent algorithmic-complexity wins and should be read with their denominator.

## Measured Surfaces

| Operator/workflow | API surface | Partner scope | Representative result | How to read it |
| --- | --- | --- | ---: | --- |
| Fixed-radius count threshold | `v4_fixed_radius_count_threshold_2d_device_arrays` | Torch CUDA | `1.697x` | Operator-level row. |
| Closest-hit grouped argmin | `v4_closest_hit_grouped_argmin_3d_device_arrays` | Torch CUDA | `1.257x` | Operator-level row. |
| Ray/triangle any-hit flags | `v4_ray_triangle_any_hit_flags_2d_device_arrays` | Torch CUDA | `5.671x` | Operator-level row. |
| Primitive grouped-i64 reduction | `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays` | Torch CUDA | `1.384x` | Operator-level row. |
| Point-group nearest witness | `v4_point_group_nearest_witness_2d_device_arrays` | Torch CUDA | `389.707x` | Large scale-dependent indexed-search win. |
| Ray/triangle any-hit weighted sum | `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` | Torch CUDA | `1.482x` | Comparable-route operator row. |
| Fixed-radius graph component union | `v4_fixed_radius_graph_component_union_3d_device_arrays` | Numba | `1.203x` | Constrained component-union route. |
| AABB all-ops count | `v4_aabb_index_query_2d_all_ops_count_prepared_runner` | RTDL native | `164.716x` | Large scale-dependent indexed-control win. |
| Aggregate-frontier device columns | `v4_aggregate_frontier_device_columns_2d_prepared_runner` | RTDL native + explicit CuPy continuation | `310.024x` over the V2.14 hot path; `0.998x` versus V3.0.2 | V2.14 host-frontier bottleneck removal; similar speed to V3. |
| Custom predicate early-exit | `v4_ray_triangle_custom_predicate_early_exit_3d_numba` | Numba C-ABI predicate | `4.633x` | V4-specific workflow for constrained predicates. |

## Plan Before Running

```python
import rtdsl.v4 as rtdl_v4

plan = rtdl_v4.plan_operator_request_v4("grouped_i64", partner="torch")
print(plan.status)
print(plan.api_surface)
```

## Request Names

Use these request names with `plan_operator_request_v4`:

| Request | Typical partner | Public surface |
| --- | --- | --- |
| `fixed_radius` | `torch` | `v4_fixed_radius_count_threshold_2d_device_arrays` |
| `closest_hit_argmin` | `torch` | `v4_closest_hit_grouped_argmin_3d_device_arrays` |
| `any_hit` | `torch` | `v4_ray_triangle_any_hit_flags_2d_device_arrays` |
| `grouped_i64` | `torch` | `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays` |
| `point_group_nearest` | `torch` | `v4_point_group_nearest_witness_2d_device_arrays` |
| `weighted_sum` | `torch` | `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` |
| `component_union` | `numba` | `v4_fixed_radius_graph_component_union_3d_device_arrays` |
| `aabb_index_query` | `rtdl_native` | `v4_aabb_index_query_2d_all_ops_count_prepared_runner` |
| `aggregate_frontier` | `rtdl_native` | `v4_aggregate_frontier_device_columns_2d_prepared_runner` |
| `grouped_sum` | `cupy` | `prepare_grouped_vector_sum_2d_partner_columns_session(partner='cupy')` |
| `custom_predicate_early_exit` | `numba` | `v4_ray_triangle_custom_predicate_early_exit_3d_numba` |

The request name describes the generic relation or continuation. The app name
stays outside the operator. For example, Triangle counting and Robot collision
can both ask for `any_hit`, then interpret the result differently in app code.

Requests outside the current V4.0 surface return a bounded planner result.
Arbitrary Python callbacks, dynamic allocation, variable-length mutation, raw
OptiX callbacks, and PTX/module linking are not V4.0 public APIs.

## Examples

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\simple\fixed_radius_torch_device_arrays.py --dry-run
py -3 examples\simple\closest_hit_grouped_argmin_torch_device_arrays.py --dry-run
py -3 examples\simple\ray_triangle_any_hit_flags_torch_device_arrays.py --dry-run
py -3 examples\simple\primitive_grouped_i64_reduction_torch_device_arrays.py --dry-run
py -3 examples\simple\point_group_nearest_witness_torch_device_arrays.py --dry-run
py -3 examples\simple\ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
py -3 examples\simple\aabb_index_all_ops_count.py --dry-run
py -3 examples\simple\custom_predicate_early_exit_planning.py
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/simple/fixed_radius_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/simple/closest_hit_grouped_argmin_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/simple/ray_triangle_any_hit_flags_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/simple/primitive_grouped_i64_reduction_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/simple/point_group_nearest_witness_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/simple/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/simple/aabb_index_all_ops_count.py --dry-run
PYTHONPATH=src:. python examples/simple/custom_predicate_early_exit_planning.py
```
