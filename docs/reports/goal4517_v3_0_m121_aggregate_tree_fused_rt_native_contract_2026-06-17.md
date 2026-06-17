# Goal4517 / V3 M121 Aggregate-Tree Fused RT-Native Contract

## Conclusion

M121 turns the Goal4497 Barnes-Hut finding into an app-agnostic RTDL runtime target: a fused aggregate-tree weighted-vector primitive that would accumulate directly into device vector/count columns. The current status is contract-only; the existing frontier device-column route remains valid RT-core evidence but not the final accelerated shape for this workload.

## Contract

- Primitive: `AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE`
- Contract: `generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1`
- Status: `specified_not_implemented`
- Executable today: `False`
- First backend target: `optix`
- CPU oracle: `sum_aggregate_frontier_weighted_vectors_2d`
- Partner oracle: `sum_aggregate_tree_fused_weighted_vectors_2d_numba_cuda`

## Output Columns

- `source_id:int64[source_count]`
- `vector_x:float64[source_count]`
- `vector_y:float64[source_count]`
- `visited_count:uint64[source_count]`
- `aggregate_count:uint64[source_count]`
- `exact_count:uint64[source_count]`

## Implementation Gates

| Gate | Status | Acceptance |
| --- | --- | --- |
| `native_abi_symbols` | `blocked` | OptiX prepare/run/destroy symbols exist and expose the declared device output columns. |
| `equivalence_oracles` | `blocked` | RT-native output columns match CPU and Numba CUDA references by source id. |
| `hot_path_materialization` | `blocked` | No user-visible frontier or contribution rows are emitted on the hot path. |
| `measured_route_rerank` | `blocked` | Rerank uses the same source-id keyed vector-summary contract. |

## Claim Boundary

- The runtime is not implemented by this packet.
- No RT-core speedup, whole-app speedup, public speedup, or paper-reproduction claim is authorized.
- No automatic partner selection or app-specific native engine logic is authorized.
- The next real engineering step is an OptiX backend prototype that satisfies the contract and matches both oracles.
