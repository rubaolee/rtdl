# V4 Tier-2 Operator Catalog

Status: scorecard passed; final release authorization pending.

V4's performance path is a catalog of generic fused RT operators. These are not
application-identity kernels. They are reusable continuation operators exposed
through Python front doors with explicit partner scope.

## Measured Tier-2 Surfaces

| Operator | API surface | Inputs | Outputs | Partner scope | Representative Goal4639 ratio |
| --- | --- | --- | --- | --- | --- |
| Fixed-radius count threshold | `v4_fixed_radius_count_threshold_2d_device_arrays` | Torch device point columns | Torch device `query_ids`, `neighbor_counts`, `threshold_flags` | Torch CUDA | `1.697x` |
| Closest-hit grouped argmin | `v4_closest_hit_grouped_argmin_3d_device_arrays` | Torch device triangle, ray, group, value, and index columns | Torch device `group_has_value`, `group_index`, `group_value` | Torch CUDA | `1.257x` |
| Ray/triangle any-hit flags | `v4_ray_triangle_any_hit_flags_2d_device_arrays` | Torch device triangle columns, triangle AABBs, and ray columns | Torch device `any_hit_flags` | Torch CUDA | `5.671x` |
| Primitive grouped-i64 reduction | `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays` | Torch device triangle/ray columns plus prepared primitive group/value payload | Torch device `group_counts`, `group_sums`, `group_mins`, `group_maxs` | Torch CUDA | `1.384x` |
| Point-group nearest witness | `v4_point_group_nearest_witness_2d_device_arrays` | RTDL-owned prepared search/groups plus Torch device query columns | Torch device `query_ids`, `neighbor_ids`, `distances` | Torch CUDA | `389.707x` |
| Ray/triangle any-hit weighted sum | `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` | Torch device triangle/ray columns plus Torch device `uint64` ray weights | Torch device `uint64[1]` weighted-hit sum scalar | Torch CUDA | `1.482x` |
| Fixed-radius graph component union | `v4_fixed_radius_graph_component_union_3d_device_arrays` | Numba-scoped prepared 3D clustered point route | Component label columns with canonical component signature | Numba | `1.203x` |
| AABB all-ops count | `v4_aabb_index_query_2d_all_ops_count_prepared_runner` | RTDL native prepared AABB boxes and point/box queries | Count scalars for all AABB query operations | RTDL native | `164.716x` |

There are currently no Tier-2 candidate surfaces in the V4 front door.

## Important Caveats

- The ratios above are representative frozen scorecard ratios, not
  whole-application speedup claims.
- Torch CUDA measurements are scoped to the validated RTX A5000 / OptiX 8.0 /
  driver 570.195.03 path unless a surface says otherwise.
- Component union is Numba-scoped operator coverage, not whole-app RTDBSCAN
  speedup wording.
- AABB all-ops is RTDL-native operator coverage with Embree as the
  same-contract-family control. It is not LibRTS paper reproduction or authors
  code comparison.
- Weighted sum is a comparable-route route win, not a pure kernel-vs-kernel
  speedup.
- CuPy performance is declared unmeasured for V4.
- public true-zero-copy wording is not authorized.

## Planner Boundary

The operator/callback planner routes recognized generic operators and fails
closed otherwise.

```python
import rtdsl.v4 as rtdl_v4

plan = rtdl_v4.plan_operator_request_v4("grouped_i64", partner="torch")
print(plan.status)
print(plan.api_surface)
```

Scalar custom callbacks remain Tier-3 spike-only. Action-shaped callbacks that
mutate shared state, allocate dynamically, or produce variable-length output are
rejected/deferred for V4.0.

## Evidence

- `future/v4/v4_goal4638_formal_release_scorecard_freeze_2026-06-25.md`
- `future/v4/v4_goal4639_serious_release_scorecard_pod_gate_decision_2026-06-25.md`
- `future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/summary.md`
- `future/v4/reviews/goal4639_serious_release_scorecard_pod_gate_review_record_2026-06-25.md`

## Non-Authorization

Not authorized by this catalog:

- final V4 release before Goal4642;
- broad V4 speedup wording;
- whole-application speedup wording;
- Tier-3 callback/PTX claims;
- raw OptiX callback claims;
- CuPy performance claims;
- embedding/C-ABI claims;
- non-Python host binding claims;
- application-specific native engine claims.
