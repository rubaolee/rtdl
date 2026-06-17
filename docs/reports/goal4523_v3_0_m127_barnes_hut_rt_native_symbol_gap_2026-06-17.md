# Goal4523 / V3 M127 Barnes-Hut RT-Native Symbol Gap

## Conclusion

M127 converts the Barnes-Hut RT-native future work into an auditable native-symbol gap. The generic fused weighted-vector RT-native contract exists, and the OptiX backend has traversal machinery elsewhere, but the required aggregate-tree fused prepare/run/destroy symbols and Python wrappers are still absent. Barnes-Hut RT-core wording remains blocked.

## Gate

- Native ABI symbols ready: `False`
- Python wrapper ready: `False`
- OptiX traversal proof ready: `False`
- Equivalence oracle ready: `False`
- Timing split ready: `False`

## Missing Symbols

- `rtdl_optix_prepare_aggregate_tree_fused_weighted_vector_sum_2d`
- `rtdl_optix_run_aggregate_tree_fused_weighted_vector_sum_2d`
- `rtdl_optix_destroy_aggregate_tree_fused_weighted_vector_sum_2d`

## Next Surfaces

- src/rtdsl/optix_runtime.py ctypes symbols and prepared-handle wrapper
- src/native/optix/rtdl_optix_api.cpp extern C prepare/run/destroy ABI
- src/native/optix/rtdl_optix_workloads.cpp launch/timing path with optixLaunch
- src/native/optix/rtdl_optix_core.cpp device program with optixTrace or equivalent traversal
- pod equivalence packet versus CPU/Numba fused weighted-vector references

## Boundary

- No runtime was executed.
- No current Barnes-Hut route changed.
- No RT-core speedup, public speedup, or automatic partner-selection wording is authorized.
