# Goal4526 / V3 M130 Barnes-Hut RT-Native Fail-Closed ABI

## Conclusion

M130 removes the missing-symbol cliff for the Barnes-Hut RT-native path by adding the app-agnostic native prepare/run/destroy ABI and matching Python bindings. The symbols intentionally fail closed: native execution, OptiX traversal proof, equivalence, timing split, and RT-core wording remain blocked until the scaffold is replaced with a real optixLaunch/optixTrace implementation.

## Gate

- Native ABI symbols exported: `True`
- Native execution ready: `False`
- OptiX traversal proof ready: `False`
- Equivalence oracle ready: `False`
- Timing split ready: `False`

## Symbols

| Symbol | Declared | Defined | Python wrapper |
| --- | --- | --- | --- |
| `rtdl_optix_prepare_aggregate_tree_fused_weighted_vector_sum_2d` | `True` | `True` | `True` |
| `rtdl_optix_run_aggregate_tree_fused_weighted_vector_sum_2d` | `True` | `True` | `True` |
| `rtdl_optix_destroy_aggregate_tree_fused_weighted_vector_sum_2d` | `True` | `True` | `True` |

## Boundary

- No runtime was executed.
- No current Barnes-Hut route changed.
- No RT-core speedup, public speedup, or automatic partner-selection wording is authorized.
