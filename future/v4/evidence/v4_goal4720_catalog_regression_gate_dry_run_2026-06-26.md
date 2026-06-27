# V4 Catalog Regression Gate

Status: generated V4.0.0 catalog gate

- mode: `dry-run`
- status: `passed`
- release authorized: `False`

| Example | Status | Passed |
| --- | --- | --- |
| `fixed_radius` | `dry_run` | `True` |
| `closest_hit_grouped_argmin` | `dry_run` | `True` |
| `ray_triangle_any_hit_flags` | `dry_run` | `True` |
| `primitive_grouped_i64_reduction` | `dry_run` | `True` |
| `point_group_nearest_witness` | `dry_run` | `True` |
| `ray_triangle_any_hit_weighted_sum` | `dry_run` | `True` |
| `aabb_index_all_ops_count` | `dry_run` | `True` |
| `v4_frontdoor_quickstart` | `ok` | `True` |
| `custom_predicate_early_exit_planning` | `ok` | `True` |
| `operator_callback_planning_tier2` | `tier2_measured_ready` | `True` |
| `operator_callback_planning_scalar_callback` | `tier3_spike_only_not_v4_0_release_surface` | `True` |
| `operator_callback_planning_complex_callback` | `rejected_action_shaped_callback_deferred` | `True` |

## Non-Authorization

This gate does not authorize broad speedup wording, whole-application speedups, Tier-3 callback/PTX support, raw OptiX callbacks, CuPy performance claims, embedding/C-ABI, non-Python host binding claims, or app-specific native kernels.
