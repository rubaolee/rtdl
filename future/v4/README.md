# RTDL V4 Front Door

Status: scorecard passed; final release authorization pending.

V4 is the Python GPU-array RT-core lane. If your program already owns Torch CUDA
arrays, RTDL accepts those arrays for measured generic fused RT operators and
writes documented outputs through the selected V4 surface. Python row objects
and host result-table downloads stay out of the hot path for the measured
surfaces that say so.

Use one import:

```python
import rtdsl.v4 as rtdl_v4
```

Current front-door status:

- measured Tier-2 surfaces: `8`
- measured partners: `numba`, `rtdl_native`, `torch`
- candidate Tier-2 surfaces: `0`
- Goal4639 scorecard: `8/8` surfaces passed, `4/4` strong families passed
- final release authorization: pending Goal4642

## Measured V4 Tier-2 Operators

| Operator | API surface | Partner scope | Representative Goal4639 ratio |
| --- | --- | --- | --- |
| Fixed-radius count-threshold | `v4_fixed_radius_count_threshold_2d_device_arrays` | Torch CUDA | `1.697x` |
| Closest-hit grouped argmin | `v4_closest_hit_grouped_argmin_3d_device_arrays` | Torch CUDA | `1.257x` |
| Ray/triangle any-hit flags | `v4_ray_triangle_any_hit_flags_2d_device_arrays` | Torch CUDA | `5.671x` |
| Primitive grouped-i64 reduction | `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays` | Torch CUDA | `1.384x` |
| Point-group nearest witness | `v4_point_group_nearest_witness_2d_device_arrays` | Torch CUDA | `389.707x` |
| Ray/triangle any-hit weighted sum | `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` | Torch CUDA | `1.482x` |
| Fixed-radius graph component union | `v4_fixed_radius_graph_component_union_3d_device_arrays` | Numba | `1.203x` |
| AABB all-ops count | `v4_aabb_index_query_2d_all_ops_count_prepared_runner` | RTDL native | `164.716x` |

These are operator-scorecard rows, not whole-application speedup claims.

List them programmatically:

```python
for row in rtdl_v4.measured_operator_catalog_v4():
    print(row["operator"], row["api_surface"], row["measured_partners"])
```

Plan a request before building a route:

```python
plan = rtdl_v4.plan_operator_request_v4("any-hit", partner="torch")
print(plan.status)
print(plan.api_surface)
```

## Complex Callback Boundary

V4.0 does not expose raw OptiX callbacks. Complex user logic is handled by a
strict planner:

- recognized generic operators route to measured Tier-2 surfaces;
- scalar Numba device callbacks remain Tier-3 spike-only, not supported V4.0
  release surfaces;
- action-shaped callbacks that mutate shared state, allocate dynamically, or
  produce variable-length output are rejected/deferred for V4.0.

The falsifiable Tier-3 callback protocol is
`future/v4/tier3_callback_spike_protocol_2026-06-24.md`. It is a spike protocol,
not a support announcement.

## Run The Public Examples

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\v4\v4_frontdoor_quickstart.py
py -3 examples\v4\operator_callback_planning.py --case complex-callback
py -3 examples\v4\primitive_grouped_i64_reduction_torch_device_arrays.py --dry-run
py -3 examples\v4\point_group_nearest_witness_torch_device_arrays.py --dry-run
py -3 examples\v4\ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
py -3 examples\v4\aabb_index_all_ops_count.py --dry-run
py -3 scripts\v4_catalog_regression_gate.py --mode dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/v4/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python examples/v4/operator_callback_planning.py --case complex-callback
PYTHONPATH=src:. python examples/v4/primitive_grouped_i64_reduction_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/point_group_nearest_witness_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/aabb_index_all_ops_count.py --dry-run
PYTHONPATH=src:. python scripts/v4_catalog_regression_gate.py --mode dry-run
```

## Evidence

Reviewer evidence:

- `future/v4/v4_goal4638_formal_release_scorecard_freeze_2026-06-25.md`
- `future/v4/v4_goal4639_serious_release_scorecard_pod_gate_decision_2026-06-25.md`
- `future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/summary.md`
- `future/v4/reviews/goal4639_serious_release_scorecard_pod_gate_review_record_2026-06-25.md`

Operator details:

- `future/v4/tier2_operator_catalog.md`
- `future/v4/fixed_radius_device_array_frontdoor.md`
- `future/v4/ray_triangle_device_array_frontdoor.md`
- `future/v4/point_group_device_array_frontdoor.md`
- `future/v4/callback_and_operator_planning.md`
- `future/v4/v4_0_scope_gate.md`

## Non-Claims

This page does not authorize:

- final V4 release before Goal4642;
- broad V4 speedup wording;
- whole-application speedup wording;
- public true-zero-copy claims;
- Tier-3 callback/PTX support claims;
- raw OptiX callback support;
- CuPy performance claims;
- embedding/C-ABI claims;
- non-Python host binding claims;
- app-specific native engine kernels.
