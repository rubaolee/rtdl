# V4 Primitive Grouped-I64 Device Outputs POD Gate

Date: 2026-06-24
Status: RTX POD candidate gate passed; external review still required before catalog promotion

## Surface

`v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`

This is a V4 Tier-2 candidate promoted from the V2/V2.x generic
`RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D` primitive. It is still not a
V4 release surface until external review and a release decision explicitly
promote it.

## Environment

- Host: `0256b71980f1`
- GPU: NVIDIA RTX A5000
- Driver: 570.195.03
- Python: 3.12.3
- Torch: 2.8.0+cu128
- CUDA prefix: `/usr/local/cuda-12.8`
- OptiX headers: `/workspace/vendor/optix-dev-8.0.0`

The POD was built with OptiX 8.0 headers because the same machine rejected the
OptiX 9.1 ABI on driver 570.

## Gate

Command:

```bash
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so PYTHONPATH=src:. \
python3 scripts/v4_primitive_grouped_i64_device_outputs_validation.py \
  --ray-counts 32768,131072 \
  --repeat 7 \
  --warmup 2 \
  --progress \
  --json-out future/v4/evidence/v4_primitive_grouped_i64_device_outputs_pod_gate_32768_131072_2026-06-24.json
```

## Result

| Rays / triangles | Groups | Parity | Device-output median (s) | Legacy host-output median (s) | Same-contract ratio |
| --- | ---: | --- | ---: | ---: | ---: |
| 32,768 | 2,048 | pass for `sum_count`, `min`, `max` | 0.000168864 | 0.001339529 | 7.933x |
| 131,072 | 8,192 | pass for `sum_count`, `min`, `max` | 0.000212841 | 0.004864600 | 22.856x |

The ratio is `legacy_host_output / direct_device_output` for the same prepared
native primitive. It measures the candidate route's removal of grouped-row host
materialization and direct writing into caller-owned Torch CUDA output columns.
It is not a broad V4 speedup claim and not a whole-application benchmark.

## Metadata Boundary

The JSON evidence records:

- `candidate_status: candidate_measured_requires_external_review_before_release_scope`
- `partner_claim_status: pod_measured_candidate_external_review_required`
- `pod_candidate_partners: ["torch"]`
- `partner_support_declared_unmeasured: ["cupy"]`
- `native_direct_device_output_columns: true`
- `host_materialization_in_hot_path: false`
- `group_rows_downloaded_to_host_in_hot_path: false`
- `python_ray_object_boundary_in_hot_path: false`
- `release_claim_authorized: false`
- `broad_v4_speedup_claim_authorized: false`
- `whole_app_speedup_claim_authorized: false`
- `tier3_callback_claim_authorized: false`

## Source Evidence

- `future/v4/evidence/v4_primitive_grouped_i64_device_outputs_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_primitive_grouped_i64_torch_device_arrays_example_result_pod_2026-06-24.json`
- `future/v4/evidence/v4_catalog_regression_gate_gpu_32768_include_candidates_point_group_2026-06-24.json`
- `future/v4/evidence/v4_catalog_regression_gate_gpu_32768_include_candidates_point_group_2026-06-24.md`

## What This Proves

- The native direct-device-output symbol builds and runs on RTX hardware.
- The V4 Python front door accepts Torch CUDA device columns and returns grouped
  output columns on device.
- Correctness matches both the older host-output primitive and the analytic
  fixture for `sum_count`, `min`, and `max`.
- The hot run keeps grouped outputs on device rather than materializing grouped
  rows to host.

## What This Does Not Prove

- It does not authorize V4 release.
- It does not make this a measured V4.0 catalog surface by itself.
- It does not authorize broad V4 speedup, whole-app speedup, true-zero-copy,
  Tier-3 callback, CuPy performance, C ABI, embedding, or non-Python host claims.
- It does not replace external review.
