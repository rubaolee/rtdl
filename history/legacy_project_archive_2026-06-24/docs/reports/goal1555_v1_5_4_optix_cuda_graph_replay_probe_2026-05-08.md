# Goal 1555 CUDA Graph Replay Feasibility Probe

## Verdict

CUDA graph replay is promising only for batched command replay in this probe.

## Scope

- Probe: repeated CUDA driver memset calls versus replaying a captured CUDA graph.
- Library: `build/librtdl_optix.so`
- Repeats: `20000`

## Result

| commands per replay | direct ms | graph ms | direct us/replay | graph us/replay | direct/graph |
|---:|---:|---:|---:|---:|---:|
| 1 | 33.549103 | 41.812512 | 1.677455 | 2.090626 | 0.802x |
| 4 | 136.524054 | 126.256458 | 6.826203 | 6.312823 | 1.081x |
| 8 | 269.166945 | 241.430325 | 13.458347 | 12.071516 | 1.115x |
| 16 | 538.777420 | 467.484224 | 26.938871 | 23.374211 | 1.153x |

Best direct-over-graph speedup: `1.153x` at `16` commands per replay.

## Claim Boundary

CUDA graph replay feasibility only; not a COLLECT_K_BOUNDED measurement and does not authorize a collect-k speedup claim.
