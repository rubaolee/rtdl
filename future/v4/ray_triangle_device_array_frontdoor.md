# V4 Ray/Triangle Device-Array Front Door

Status: measured V4 surface; final release authorization pending

This page documents the measured V4 Tier-2 ray/triangle primitive surfaces:

- `v4_closest_hit_grouped_argmin_3d_device_arrays`
- `v4_ray_triangle_any_hit_flags_2d_device_arrays`
- `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
- `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`

The user contract is direct: if your program already owns GPU arrays, RTDL
should accept those arrays, run a generic RT primitive, and write the result
back into GPU arrays you own. No Python ray rows or result-table host downloads
sit in the hot path.

## Closest-Hit Grouped Argmin API

Use the V4 module surface directly:

```python
import rtdsl.v4_ray_triangle as rt_v4

with rt_v4.prepare_closest_hit_grouped_argmin_3d_device_arrays_v4(
    triangle_columns,
    ray_columns,
    per_ray_group_ids=per_ray_group_ids,
    candidate_values=candidate_values,
    candidate_indices=candidate_indices,
    group_count=group_count,
    partner="torch",
) as session:
    output_columns = session.allocate_outputs()
    result = session.run(output_columns=output_columns, return_metadata=True)
```

Required triangle columns:

- `ids`: `torch.uint32`, CUDA, contiguous, one-dimensional
- `x0`, `y0`, `z0`: `torch.float64`, CUDA, contiguous
- `x1`, `y1`, `z1`: `torch.float64`, CUDA, contiguous
- `x2`, `y2`, `z2`: `torch.float64`, CUDA, contiguous

Required ray columns:

- `ids`: `torch.uint32`, CUDA, contiguous
- `ox`, `oy`, `oz`: `torch.float64`, CUDA, contiguous
- `dx`, `dy`, `dz`: `torch.float64`, CUDA, contiguous
- `tmax`: `torch.float64`, CUDA, contiguous

Required grouped-argmin columns:

- `per_ray_group_ids`: `torch.uint32`, CUDA, contiguous
- `candidate_values`: `torch.float64`, CUDA, contiguous
- `candidate_indices`: `torch.uint32`, CUDA, contiguous

Output columns:

- `group_has_value`: `torch.uint8`, CUDA
- `group_index`: `torch.uint32`, CUDA
- `group_value`: `torch.float64`, CUDA

## Any-Hit Flags API

Use the 2-D any-hit flag surface when each caller-owned ray needs one
`uint32` hit/no-hit flag:

```python
import rtdsl.v4_ray_triangle as rt_v4

with rt_v4.prepare_ray_triangle_any_hit_flags_2d_device_arrays_v4(
    triangle_columns,
    triangle_aabbs,
    partner="torch",
) as session:
    output_flags = session.allocate_outputs(ray_count)
    result = session.run(ray_columns, output_flags=output_flags, return_metadata=True)
```

Required 2-D triangle columns:

- `ids`: `torch.uint32`, CUDA, contiguous, one-dimensional
- `x0`, `y0`: `torch.float64`, CUDA, contiguous
- `x1`, `y1`: `torch.float64`, CUDA, contiguous
- `x2`, `y2`: `torch.float64`, CUDA, contiguous

Required triangle AABBs:

- shape `(triangle_count, 6)`, `torch.float32`, CUDA, contiguous

Required 2-D ray columns:

- `ids`: `torch.uint32`, CUDA, contiguous
- `ox`, `oy`: `torch.float64`, CUDA, contiguous
- `dx`, `dy`: `torch.float64`, CUDA, contiguous
- `tmax`: `torch.float64`, CUDA, contiguous

Output:

- `any_hit_flags`: `torch.uint32`, CUDA, one flag per ray

## Primitive Grouped-I64 Reduction API

This measured surface promotes the V2/V2.x generic
`RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D` primitive into the V4 front
door. Its measured scope is Torch CUDA on OptiX 8.0 / RTX A5000. OptiX 9.1,
CuPy performance, broad V4 speedup wording, whole-app speedup wording, and
public true-zero-copy wording remain unauthorized.

```python
import rtdsl.v4_ray_triangle as rt_v4

with rt_v4.prepare_primitive_grouped_i64_reduction_3d_device_arrays_v4(
    triangle_columns,
    ray_columns,
    primitive_group_ids=primitive_group_ids,
    primitive_values=primitive_values,
    group_count=group_count,
    partner="torch",
) as session:
    output_columns = session.allocate_outputs()
    result = session.run(reduction="sum", output_columns=output_columns)
```

Required output columns:

- `group_counts`: `torch.uint64`, CUDA
- `group_sums`: `torch.uint64`, CUDA
- `group_mins`: `torch.uint64`, CUDA
- `group_maxs`: `torch.uint64`, CUDA

Current boundary:

- ray and triangle inputs are Torch CUDA device columns
- grouped output columns are Torch CUDA device columns
- primitive group/value payload is prepared once, outside the hot run
- the native library must be rebuilt with
  `rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction_device_outputs`
- RTX A5000 POD correctness/performance evidence exists for group widths 1, 16,
  and 256

## Any-Hit Weighted-Sum API

This measured surface exposes the existing RT-core-backed device-output graph
executor through a V4 Torch device-array front door:

```python
import rtdsl.v4_ray_triangle as rt_v4

with rt_v4.prepare_ray_triangle_any_hit_weighted_sum_3d_device_arrays_v4(
    triangle_columns,
    ray_columns,
    ray_weights,
    partner="torch",
) as session:
    result = session.run(return_metadata=True)
    weighted_sum = result["columns"]["weighted_hit_sum"]
```

Required additional input:

- `ray_weights`: `torch.uint64`, CUDA, contiguous, one value per prepared ray

Output:

- `weighted_hit_sum`: `torch.uint64`, CUDA, shape `(1,)`

Current boundary:

- ray and triangle inputs are Torch CUDA device columns
- ray weights are Torch CUDA device columns
- the primary output path uses an RTDL-allocated Torch CUDA scalar; a
  caller-supplied scalar override is supported
- metadata records `device_output_used: true`,
  `host_scalar_read_before_consumer: false`, and
  `surface_status: tier2_measured_pod_validated_not_release`
- Goal4633 promoted the surface after the RTX A5000 comparable-route gate

## Minimal Examples

Run on a CUDA/OptiX machine:

```bash
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=/path/to/librtdl_optix.so
python examples/v4/closest_hit_grouped_argmin_torch_device_arrays.py --ray-count 8192
python examples/v4/ray_triangle_any_hit_flags_torch_device_arrays.py --ray-count 8192
python examples/v4/primitive_grouped_i64_reduction_torch_device_arrays.py --ray-count 8192
python examples/v4/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --ray-count 8192
```

Dry-run locally without CUDA:

```bash
python examples/v4/closest_hit_grouped_argmin_torch_device_arrays.py --dry-run
python examples/v4/ray_triangle_any_hit_flags_torch_device_arrays.py --dry-run
python examples/v4/primitive_grouped_i64_reduction_torch_device_arrays.py --dry-run
python examples/v4/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
```

## Evidence

Closest-hit grouped-argmin measured RTX POD result:

| rays | triangles | groups | V4 direct device-array median | legacy host-materialize median | ratio |
|---:|---:|---:|---:|---:|---:|
| 8,192 | 8,192 | 1,024 | 0.000092s | 0.000142s | 1.542x |
| 32,768 | 32,768 | 4,096 | 0.000102s | 0.000161s | 1.575x |
| 131,072 | 131,072 | 16,384 | 0.000125s | 0.000217s | 1.729x |

Source evidence:

- `future/v4/evidence/v4_section8_closest_hit_grouped_argmin_device_frontdoor_result_2026-06-24.json`
- `future/v4/evidence/v4_section8_closest_hit_grouped_argmin_device_frontdoor_report_2026-06-24.md`

The evidence metadata records `native_direct_device_output_columns: true`,
`grouped_result_device_to_device_export: false`, and
`grouped_results_downloaded_to_host_in_hot_path: false`.

Grouped argmin does not carry a public `true_zero_copy_authorized` claim in
V4.0. It is still a measured device-array surface: inputs and grouped outputs
stay in caller-owned Torch CUDA columns for the hot path, but the prepared
grouped inputs and OptiX traversal use internal device-side staging that is
disclosed in the evidence instead of hidden behind stronger zero-copy wording.

Any-hit flags evidence is tracked separately:

- `future/v4/evidence/v4_section8_any_hit_flags_device_frontdoor_result_2026-06-24.json`
- `future/v4/evidence/v4_section8_any_hit_flags_device_frontdoor_report_2026-06-24.md`

That surface records `native_direct_device_output_columns: true`,
`ray_results_downloaded_to_host_in_hot_path: false`, and
`host_materialization_in_hot_path: false`.

Primitive grouped-i64 reduction local gate:

| rays | triangles | groups | direct device-output median | legacy host-output median | local ratio |
|---:|---:|---:|---:|---:|---:|
| 8,192 | 8,192 | 512 | 0.000131s | 0.000358s | 2.737x |
| 32,768 | 32,768 | 2,048 | 0.000196s | 0.001057s | 5.391x |

Source evidence:

- `future/v4/evidence/v4_primitive_grouped_i64_device_outputs_lx1_local_gate_2026-06-24.md`
- `future/v4/evidence/v4_primitive_grouped_i64_device_outputs_lx1_local_gate_8192_32768_2026-06-24.json`
- `future/v4/evidence/v4_primitive_grouped_i64_torch_device_arrays_example_result_2026-06-24.json`

This local evidence is supporting evidence; the measured catalog scope is based
on the RTX A5000 POD evidence below.

Primitive grouped-i64 reduction RTX POD gate:

| rays | triangles | groups | direct device-output median | legacy host-output median | same-contract ratio |
|---:|---:|---:|---:|---:|---:|
| 32,768 | 32,768 | 2,048 | 0.000169s | 0.001340s | 7.933x |
| 131,072 | 131,072 | 8,192 | 0.000213s | 0.004865s | 22.856x |

Source evidence:

- `future/v4/evidence/v4_primitive_grouped_i64_device_outputs_pod_gate_32768_131072_2026-06-24.md`
- `future/v4/evidence/v4_primitive_grouped_i64_device_outputs_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_primitive_grouped_i64_torch_device_arrays_example_result_pod_2026-06-24.json`

Additional group-width POD evidence:

| group width | rays | groups | direct device-output median | legacy host-output median | same-contract ratio |
|---:|---:|---:|---:|---:|---:|
| 1 | 32,768 | 32,768 | 0.000183s | 0.030539s | 166.546x |
| 1 | 131,072 | 131,072 | 0.000377s | 0.155330s | 411.867x |
| 16 | 32,768 | 2,048 | 0.000147s | 0.001662s | 11.271x |
| 16 | 131,072 | 8,192 | 0.000223s | 0.004758s | 21.369x |
| 256 | 32,768 | 128 | 0.000145s | 0.000238s | 1.641x |
| 256 | 131,072 | 512 | 0.000419s | 0.001248s | 2.978x |

Source evidence:

- `future/v4/evidence/v4_goal4617_grouped_i64_width1_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_goal4617_grouped_i64_width16_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_goal4617_grouped_i64_width256_pod_gate_32768_131072_2026-06-24.json`

These ratios are same-contract operator comparisons against the older
host-output primitive. They are not broad V4 speedup wording.

Ray/triangle any-hit weighted-sum measured RTX POD gate:

| rays | triangles | device-output median | host-scalar median | same-contract ratio |
|---:|---:|---:|---:|---:|
| 32,768 | 32,768 | 0.000068s | 0.000139s | 2.047x |
| 131,072 | 131,072 | 0.000147s | 0.000228s | 1.557x |

Source evidence:

- `future/v4/evidence/v4_goal4620_ray_triangle_weighted_sum_pod_gate_32768_131072_2026-06-24.md`
- `future/v4/evidence/v4_goal4620_ray_triangle_weighted_sum_pod_gate_32768_131072_2026-06-24.json`

Goal4633 promoted this surface to measured catalog status after the 2026-06-25
weighted-sum promotion gate. The Goal4639 scorecard re-ran the surface and
recorded a representative ratio of `1.482x`.

## Important Boundary

This validates a generic RT primitive surface, not an application-specific
Barnes-Hut, DBSCAN, or ray-join kernel. The fused continuation is grouped
argmin or any-hit flag output, both reusable operator-level primitives.

CuPy is declared but unmeasured for these surfaces. Torch is the measured
partner for the ray/triangle V4 surfaces on the documented POD gates.

## Non-Claims

This page does not authorize:

- final V4 release before Goal4642
- broad V4 speedup wording
- whole-application speedup wording
- Tier-3 callback/PTX claims
- true-zero-copy public wording
- app-specific native engine claims
