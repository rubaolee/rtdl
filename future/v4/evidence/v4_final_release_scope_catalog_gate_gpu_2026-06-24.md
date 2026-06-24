# V4 Catalog Regression Gate

Status: generated development gate, not a release authorization

- mode: `gpu`
- status: `passed`
- release authorized: `False`

| Example | Status | Passed |
| --- | --- | --- |
| `fixed_radius` | `measured` | `True` |
| `closest_hit_grouped_argmin` | `measured` | `True` |
| `ray_triangle_any_hit_flags` | `measured` | `True` |
| `v4_frontdoor_quickstart` | `ok` | `True` |
| `operator_callback_planning_tier2` | `tier2_measured_ready` | `True` |
| `operator_callback_planning_scalar_callback` | `tier3_spike_only_not_v4_0_release_surface` | `True` |
| `operator_callback_planning_complex_callback` | `rejected_action_shaped_callback_deferred` | `True` |

## Non-Authorization

This gate does not authorize V4 release, broad speedup wording, Tier-3 callback/PTX support, raw OptiX callbacks, embedding/C-ABI, or app-specific native kernels.
