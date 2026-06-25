# V4 `goal4620` Ray/Triangle Any-Hit Weighted-Sum POD Gate

Status: candidate evidence, not a release authorization

Source JSON:

- `future/v4/evidence/v4_goal4620_ray_triangle_weighted_sum_pod_gate_32768_131072_2026-06-24.json`

## Scope

- Surface: `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`
- Status: `tier2_candidate_goal4620_not_measured`
- Hardware: NVIDIA RTX A5000
- Driver: 570.195.03
- Partner: Torch CUDA (`torch 2.8.0+cu128`)
- OptiX ABI scope: 8.0 only
- Sizes: 32768 and 131072 rays/triangles
- Repeats: 5 measured repeats after 2 warmups

## Result

| Rays | Parity | Device-Output Median (s) | Host-Scalar Median (s) | Same-Contract Ratio |
|---:|---|---:|---:|---:|
| 32768 | true | 0.000068050 | 0.000139300 | 2.047x |
| 131072 | true | 0.000146613 | 0.000228226 | 1.557x |

The ratio is `host_scalar_route_median / device_output_frontdoor_median`.
It is a candidate-level same-contract comparison against the existing
host-scalar weighted-sum route. It does not authorize broad V4 performance
wording, whole-app speedup wording, release wording, or measured-catalog
promotion.

## Metadata Gates Observed

- `device_output_used: true`
- `host_scalar_read_before_consumer: false`
- `host_row_materialization_before_consumer: false`
- `query_rays_uploaded_each_run: false`
- `ray_weights_uploaded_each_run: false`
- `cuda_stream_ptr_nonzero: true`
- `surface_status: tier2_candidate_goal4620_not_measured`
- `true_zero_copy_authorized: false`
- `release_claim_authorized: false`
- `broad_v4_speedup_claim_authorized: false`
- `whole_app_speedup_claim_authorized: false`
- `tier3_callback_claim_authorized: false`

## Non-Authorization

This evidence does not authorize:

- V4 release
- measured-catalog promotion
- broad V4 speedup claims
- whole-application speedup claims
- true-zero-copy wording
- OptiX 9.1 scope
- CuPy performance claims
- Tier-3 callback work
- C ABI / embedding / non-Python-host work
- app-specific native kernels

