# V4 Goal4639 Serious Release Scorecard POD Gate

Status: `goal4639_serious_release_scorecard_pod_gate_not_release`

Recommendation: `release_candidate_possible_pending_3ai`

## Summary

- strong families passed: `4/4`
- measured surfaces passed: `8/8`
- partial controls passed: `4/4`
- deferred/excluded rows: `2`
- strong representative ratio geomean: `5.1848067367961095`
- failed surfaces: `none`

## Surface Results

| Surface | Status | Representative ratio | Failure |
| --- | --- | ---: | --- |
| `v4_fixed_radius_count_threshold_2d_device_arrays` | `pass` | 1.69721x |  |
| `v4_closest_hit_grouped_argmin_3d_device_arrays` | `pass` | 1.25677x |  |
| `v4_ray_triangle_any_hit_flags_2d_device_arrays` | `pass` | 5.67055x |  |
| `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays` | `pass` | 1.38362x |  |
| `v4_point_group_nearest_witness_2d_device_arrays` | `pass` | 389.707x |  |
| `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` | `pass` | 1.48181x |  |
| `v4_fixed_radius_graph_component_union_3d_device_arrays` | `pass` | 1.20294x |  |
| `v4_aabb_index_query_2d_all_ops_count_prepared_runner` | `pass` | 164.716x |  |

## Benchmark Family Rows

| Family | Class | Passed | Surfaces |
| --- | --- | --- | --- |
| `rt_dbscan` | `release_in_scope_strong_operator` | `True` | `v4_fixed_radius_count_threshold_2d_device_arrays`, `v4_fixed_radius_graph_component_union_3d_device_arrays` |
| `raydb_style` | `release_in_scope_strong_operator` | `True` | `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`, `v4_closest_hit_grouped_argmin_3d_device_arrays`, `v4_ray_triangle_any_hit_flags_2d_device_arrays` |
| `triangle_counting` | `release_in_scope_strong_operator` | `True` | `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`, `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays` |
| `librts_spatial_index` | `release_in_scope_strong_operator` | `True` | `v4_aabb_index_query_2d_all_ops_count_prepared_runner` |
| `hausdorff_xhd` | `partial_operator_control` | `True` | `v4_point_group_nearest_witness_2d_device_arrays`, `v4_fixed_radius_count_threshold_2d_device_arrays` |
| `robot_collision` | `partial_operator_control` | `True` | `v4_ray_triangle_any_hit_flags_2d_device_arrays` |
| `contact_manifold` | `partial_operator_control` | `True` | `v4_point_group_nearest_witness_2d_device_arrays` |
| `rtnn` | `partial_operator_control` | `True` | `v4_point_group_nearest_witness_2d_device_arrays` |
| `spatial_rayjoin` | `deferred_excluded` | `None` | none |
| `barnes_hut` | `deferred_excluded` | `None` | none |

## Command Records

### fixed_radius_count_threshold

- surface: `v4_fixed_radius_count_threshold_2d_device_arrays`
- return code: `0`
- elapsed seconds: `5.067`

```bash
/usr/bin/python3 scripts/v4_section8_device_array_frontdoor_validation.py --partner torch --repeat 7 --warmup 1 --progress --json-out future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/fixed_radius_count_threshold.json
```

### closest_hit_grouped_argmin

- surface: `v4_closest_hit_grouped_argmin_3d_device_arrays`
- return code: `0`
- elapsed seconds: `4.042`

```bash
/usr/bin/python3 scripts/v4_section8_closest_hit_grouped_argmin_device_frontdoor_validation.py --repeat 7 --warmup 1 --progress --json-out future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/closest_hit_grouped_argmin.json
```

### ray_triangle_any_hit_flags

- surface: `v4_ray_triangle_any_hit_flags_2d_device_arrays`
- return code: `0`
- elapsed seconds: `4.000`

```bash
/usr/bin/python3 scripts/v4_section8_any_hit_flags_device_frontdoor_validation.py --repeat 5 --warmup 1 --max-torch-reference-count 8192 --progress --json-out future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/ray_triangle_any_hit_flags.json
```

### primitive_grouped_i64_width1

- surface: `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
- return code: `0`
- elapsed seconds: `6.724`

```bash
/usr/bin/python3 scripts/v4_primitive_grouped_i64_device_outputs_validation.py --ray-counts 32768,131072 --group-width 1 --repeat 7 --warmup 2 --progress --json-out future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/primitive_grouped_i64_width1.json
```

### primitive_grouped_i64_width16

- surface: `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
- return code: `0`
- elapsed seconds: `4.227`

```bash
/usr/bin/python3 scripts/v4_primitive_grouped_i64_device_outputs_validation.py --ray-counts 32768,131072 --group-width 16 --repeat 7 --warmup 2 --progress --json-out future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/primitive_grouped_i64_width16.json
```

### primitive_grouped_i64_width256

- surface: `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
- return code: `0`
- elapsed seconds: `4.368`

```bash
/usr/bin/python3 scripts/v4_primitive_grouped_i64_device_outputs_validation.py --ray-counts 32768,131072 --group-width 256 --repeat 7 --warmup 2 --progress --json-out future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/primitive_grouped_i64_width256.json
```

### point_group_nearest_witness_mixed4

- surface: `v4_point_group_nearest_witness_2d_device_arrays`
- return code: `0`
- elapsed seconds: `17.879`

```bash
/usr/bin/python3 scripts/v4_point_group_nearest_witness_device_outputs_validation.py --query-counts 32768,131072 --fixture-variant mixed4 --repeat 7 --warmup 2 --progress --json-out future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/point_group_nearest_witness_mixed4.json --md-out future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/point_group_nearest_witness_mixed4.md
```

### point_group_nearest_witness_mixed6

- surface: `v4_point_group_nearest_witness_2d_device_arrays`
- return code: `0`
- elapsed seconds: `18.293`

```bash
/usr/bin/python3 scripts/v4_point_group_nearest_witness_device_outputs_validation.py --query-counts 32768,131072 --fixture-variant mixed6 --repeat 7 --warmup 2 --progress --json-out future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/point_group_nearest_witness_mixed6.json --md-out future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/point_group_nearest_witness_mixed6.md
```

### ray_triangle_any_hit_weighted_sum

- surface: `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`
- return code: `0`
- elapsed seconds: `4.407`

```bash
/usr/bin/python3 scripts/v4_ray_triangle_weighted_sum_device_output_validation.py --goal4633-promotion-gate --progress --json-out future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/ray_triangle_any_hit_weighted_sum.json --md-out future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/ray_triangle_any_hit_weighted_sum.md
```

### fixed_radius_graph_component_union

- surface: `v4_fixed_radius_graph_component_union_3d_device_arrays`
- return code: `0`
- elapsed seconds: `43.063`

```bash
/usr/bin/python3 scripts/v3_phoenix_component_union_m38_pod_ab.py --output-dir future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/fixed_radius_graph_component_union --variant all --dataset clustered3d --point-count 262144 --radius 3.0 --min-neighbors 4 --seed 20260625 --repeat 5 --warmup 1 --require-rt-hardware --heartbeat-sec 30
```

### aabb_index_all_ops_count

- surface: `v4_aabb_index_query_2d_all_ops_count_prepared_runner`
- return code: `0`
- elapsed seconds: `151.132`

```bash
/usr/bin/python3 scripts/v3_0_m30_librts_prepared_all_ops_refresh.py --box-count 1000000 --query-count 1000 --seed 2025 --max-box-width 0.005 --max-box-height 0.005 --max-query-width 0.005 --max-query-height 0.005 --operation all --backends embree,optix --warmup 1 --repeat-overrides embree=240,optix=240 --output future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/aabb_index_all_ops_count.json
```

## Non-Authorization

This scorecard does not authorize V4 release, V4 release-candidate wording,
broad V4 speedup claims, whole-app speedup claims, all-benchmark speedup
claims, public true-zero-copy claims, Tier-3 callback support, raw OptiX
callback support, CuPy performance claims, C ABI, embedding, non-Python
host claims, or app-specific native kernels.
