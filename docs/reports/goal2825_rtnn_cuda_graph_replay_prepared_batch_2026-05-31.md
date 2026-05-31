# Goal2825 RTNN CUDA Graph Replay for Prepared Batch Aggregates

Date: 2026-05-31

Verdict: accept-with-boundary.

## Purpose

Goal2825 follows the Goal2821-Goal2824 RTNN batch chain. Goal2821 added
heterogeneous prepared requests, Goal2822 fused those requests into one
block-partial batch kernel, and Goal2823 rejected a separate device partial
reduction as default because the extra launch did not pay for itself.

This goal tests the next launch-overhead reduction that Gemini recommended in
Goal2824: explicit CUDA graph replay for static prepared workloads. The target
is narrow and generic:

- prepared fixed-radius 3-D search handle;
- prepared query-points handle;
- static batch of `(radius, k_max)` aggregate requests;
- replay of the existing Goal2822 fused block-partial kernel.

No RTNN-specific native name, paper-specific algorithm, or app-specific
continuation is introduced.

## Implementation

The native OptiX backend now has an explicit prepared graph handle:

- `rtdl_optix_prepare_fixed_radius_ranked_summary_aggregate_batch_graph_3d`
- `rtdl_optix_replay_fixed_radius_ranked_summary_aggregate_batch_graph_3d`
- `rtdl_optix_destroy_fixed_radius_ranked_summary_aggregate_batch_graph_3d`

The handle owns:

- a CUDA stream;
- a captured CUDA graph;
- an instantiated `CUgraphExec`;
- device-resident static radius and `k_max` request arrays;
- the compact per-request/per-query-block partial aggregate buffer.

The graph captures only the generic
`fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_blocks_batch`
kernel. Replay then downloads the compact partial aggregate array and performs
the same host reduction used by Goal2822.

The Python runtime exposes the path as:

```python
graph = prepared.prepare_ranked_summary_prepared_queries_batch_graph(
    prepared_queries,
    requests,
    precision="float32",
)
summaries = graph.replay()
```

The benchmark runner adds result mode:

`ranked-summary-aggregate-prepared-query-batch-graph-float32`

This is opt-in. It does not change the default runtime path.

## Evidence

Pod:

- SSH command supplied by the user: `ssh root@69.30.85.171 -p 22167 -i ~/.ssh/id_ed25519`
- GPU: NVIDIA RTX A5000, driver 570.211.01
- Base source commit before applying the Goal2825 patch:
  `c542ba8006458ac9784f89418c794e72399e1b45`
- CUDA/OptiX setup: CUDA 12 build, OptiX SDK at `/root/vendor/optix-sdk`
- Artifact directory:
  `docs/reports/goal2825_rtnn_cuda_graph_replay_pod/`

Synthetic workload:

- uniform 3-D point clouds;
- 32K and 65K search/query points;
- one prepared query batch containing all query points;
- four static aggregate requests:
  `(radius, k_max) = (0.01, 8), (0.02, 16), (0.03, 32), (0.04, 50)`;
- 25 timed repeats per row.

| Points | Goal2822 Fused Batch Median (s) | Goal2825 Graph Replay Median (s) | Graph vs Fused | Result parity |
| ---: | ---: | ---: | ---: | --- |
| 32,768 | 0.000302468 | 0.000261544 | 1.156x | exact aggregate parity |
| 65,536 | 0.000829425 | 0.000808079 | 1.026x | exact aggregate parity |

The raw graph result dictionaries include `"cuda_graph_replay": true`, so the
report compares normalized computational fields. After normalization, both the
aggregate summary and per-request batch summaries match exactly.

Phase telemetry distinguishes the two paths:

- fused batch:
  `prepared_query_uniform_cell_ranked_summary_aggregate_f32_batch_block_partials`
- graph replay:
  `prepared_query_uniform_cell_ranked_summary_aggregate_f32_batch_cuda_graph_replay`

## Interpretation

CUDA graph replay helps most where launch overhead is still visible. In this
probe, that is the 32K row: graph replay is about 15.6% faster than the fused
batch path. At 65K, kernel work dominates more of the row, and graph replay is
only about 2.6% faster.

That is useful, but it is not a broad performance claim. The current default
should remain Goal2822's fused batch path until we have more repeated-static
workloads showing that graph preparation cost and static-shape constraints are
worth exposing by default.

## Claim Boundary

This goal does not authorize:

- public RTDL-beats-CuPy wording;
- public RTDL-beats-RTNN-paper wording;
- paper reproduction wording;
- whole-app speedup wording;
- broad RT-core speedup wording;
- v2.5 release wording;
- changing the default runtime path.

The accepted claim is narrower: RTDL v2.5 now has an opt-in, generic CUDA graph
replay handle for static prepared fixed-radius ranked-summary aggregate
batches, with measured exact-parity replay speedups of 1.156x at 32K and 1.026x
at 65K on the recorded RTX A5000 pod.

## Next Step

The next meaningful v2.5 runtime target is not another single-kernel
micro-reduction. It is event-ordered chaining from this prepared aggregate path
into partner consumers, or graph-node update support for repeated workloads
whose request arrays change while topology and buffer shapes remain static.

