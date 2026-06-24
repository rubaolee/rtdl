# V4 Ray/Triangle Device-Array Front Door

Status: V4 development surface, not a release announcement

This page documents the second measured V4 Tier-2 primitive surface:
closest-hit grouped argmin over caller-owned Torch CUDA triangle, ray, group,
and output columns.

The user contract is direct: if your program already owns GPU arrays, RTDL
should accept those arrays, run the generic RT primitive, and write the grouped
result back into GPU arrays you own. No Python ray rows or grouped-result host
downloads sit in the hot path.

## API Shape

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

## Minimal Example

Run on a CUDA/OptiX machine:

```bash
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=/path/to/librtdl_optix.so
python future/v4/examples/closest_hit_grouped_argmin_torch_device_arrays.py --ray-count 8192
```

Dry-run locally without CUDA:

```bash
python future/v4/examples/closest_hit_grouped_argmin_torch_device_arrays.py --dry-run
```

## Evidence

Measured RTX POD result:

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

## Important Boundary

This validates a generic RT primitive surface, not an application-specific
Barnes-Hut, DBSCAN, or ray-join kernel. The fused continuation is grouped
argmin, which is a reusable operator-level primitive.

CuPy is declared but unmeasured for this surface. Torch is the measured partner.

## Non-Claims

This page does not authorize:

- V4 release
- broad V4 speedup wording
- whole-application speedup wording
- Tier-3 callback/PTX claims
- true-zero-copy public wording
- app-specific native engine claims
