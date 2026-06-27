# v4_goal4633_ray_triangle_any_hit_weighted_sum_promotion_gate

Surface: `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`
Surface status before gate: `tier2_candidate_goal4620_not_measured`
Decision: `promote_weighted_sum_measured_torch_v4_tier2_pending_external_completion_audit`

## Route Boundary

The ratio compares the existing host-scalar materialization path against the V4 device-resident output path for the same weighted-sum operator.

This is not a pure kernel-vs-kernel speedup figure and does not authorize broad V4 or whole-application claims.

## Results

| rays | triangles | parity | device-output median (s) | host-scalar median (s) | comparable-route ratio |
|---:|---:|---|---:|---:|---:|
| 32768 | 32768 | true | 0.000075089 | 0.000161130 | 2.146x |
| 131072 | 131072 | true | 0.000143832 | 0.000234857 | 1.633x |
| 262144 | 262144 | true | 0.000243494 | 0.000330282 | 1.356x |
| 524288 | 524288 | true | 0.000436813 | 0.000524670 | 1.201x |

## Gate

- all shapes completed: `True`
- parity all passed: `True`
- no hot-path host materialization: `True`
- min ratio: `1.2011325646448796`
- geomean ratio: `1.5457333064727565`
- per-shape ratio threshold: `>=1.2x`
- geomean threshold: `>=1.5x`

## Non-Authorization

- V4 release is not authorized by this gate alone.
- Whole-application speedup claims are not authorized.
- CuPy performance claims are not authorized.
- Tier-3 callback support is not authorized.
- Public true-zero-copy wording is not authorized.
