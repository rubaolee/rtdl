# Goal1640 v1.6.x OptiX Collect-K Graph Full-Scale Diagnostic

## Verdict

`full_scale_graph_diagnostic_positive_but_insufficient`

The diagnostic CUDA graph replay and graph-update paths now run at the real single-pair final compact scale, `pair_count=1` and `segment_capacity=131072`. Both preserve the expected first-pair count and show a positive replay-only signal, but the measured gain is still too small and too isolated to justify production `COLLECT_K_BOUNDED` graph replay.

## Scope

- Code change: expanded the graph replay/update diagnostic guardrail from `512` total blocks to `4096` total blocks.
- Production effect: none. No `RTDL_OPTIX_COLLECT_K_LEVEL_GRAPH_REPLAY` runtime flag is present or enabled.
- GPU: `NVIDIA RTX A4500, 550.127.05, 20470 MiB`.
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`.
- Replay artifact: `docs/reports/goal1640_level_graph_pair1_segment131072_repeats1000.json`.
- Update artifact: `docs/reports/goal1640_level_graph_update_pair1_segment131072_repeats1000.json`.

## Result

### Graph Replay

| field | value |
| --- | ---: |
| pair_count | 1 |
| segment_capacity | 131072 |
| repeats | 1000 |
| direct_per_replay_us | 119.210037 |
| graph_per_replay_us | 107.027736 |
| direct_over_graph_speedup | 1.113824x |
| first_pair_count | 262144 |

### Graph Update

| field | value |
| --- | ---: |
| initial_pair_count | 1 |
| target_pair_count | 1 |
| segment_capacity | 131072 |
| repeats | 1000 |
| kernel_node_count | 4 |
| direct_per_replay_us | 119.258329 |
| graph_update_per_replay_us | 116.440828 |
| direct_over_graph_update_speedup | 1.024197x |
| first_pair_count | 262144 |

## Interpretation

The real-scale graph diagnostics are technically viable. This removes the previous guardrail blocker and shows that a compact four-kernel graph can replay faster than direct launches at final-pair scale.

However, this does not yet solve the Goal1637 bottleneck. Goal1637 measured roughly `0.314 ms` of host-visible wait around the final-pair mark point, while this Goal1640 graph replay only improves the isolated four-kernel replay by about `12.18 us`, and graph-update improves by about `2.82 us`. The evidence therefore points away from simply re-enabling the old per-level graph path. The next useful optimization must measure the full steady-state production dependency chain, including any host count dependency or synchronization that remains outside the isolated graph replay.

## Claim Boundary

This is internal diagnostic evidence only. It does not authorize public speedup wording, true zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup claims, release tags, or release action.
