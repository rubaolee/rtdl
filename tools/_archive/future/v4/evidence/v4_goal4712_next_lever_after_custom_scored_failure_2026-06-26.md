# V4 Goal4712 Next Lever After Custom-Scored Failure

- validation: `passed`
- status: `goal4712_next_lever_after_custom_scored_failure_selected_protocol_required`
- selected target: `custom_predicate_early_exit_multi_hit`
- next goal: `Goal4713 custom predicate early-exit multi-hit protocol freeze`

## Failure Fact

- source goal: `Goal4711`
- failed target: `ray_triangle_custom_scored_accumulation`
- classification: `fail_focused_app_gate_not_high_performance`
- primary geomean V3 speedup: `1.0289410940907995`
- min primary V3 speedup: `1.0144917291107025`

## Selected Contract

- generic feature: `constrained custom predicate callback in any-hit with RTDL-owned early-exit policy`
- app family: `ray/triangle multi-hit custom predicate early-exit`
- allowed callback shape: `pure scalar/boolean Numba C-ABI device function with no side effects`
- engine-owned action: `RTDL applies terminate_on_first_accept or count_until_threshold; user callback does not mutate external state`

Unlike post-hit accumulation, a predicate callback can affect traversal-side control flow. V4 can reject or terminate inside any-hit before materializing every candidate, while V2/V3 fallback must materialize all hit IDs or hit attributes and then run a separate device predicate/filter.

## Rejected Patterns

| pattern | reason |
|---|---|
| `post_hit_scalar_accumulation_polish` | Goal4711 already measured this shape at about 1.029x geomean; more wording or minor polish is not a new lever. |
| `weighted_sum_or_existing_operator_control` | Weighted sum exists in V2/V3 and is control-only, not V4-specific app evidence. |
| `global_atomic_scalar_accumulation` | Goal4711 smoke showed global atomic accumulation is a diagnostic control, not a performance route. |
| `same_target_rerun_without_changed_cost_model` | Rerunning the same custom-scored app cannot move the frozen bar unless the mechanism changes. |

## Non-Authorization

- POD is not authorized by Goal4712.
- V4 release is not authorized.
- Formal high-performance V4 wording is not authorized.
- Public Tier-3 support is not authorized.
- Arbitrary callback or raw OptiX callback support is not authorized.
