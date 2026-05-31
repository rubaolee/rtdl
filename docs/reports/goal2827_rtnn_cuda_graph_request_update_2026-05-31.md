# Goal2827 RTNN CUDA Graph Request-Buffer Update

Date: 2026-05-31

Verdict: accept-with-boundary.

## Purpose

Goal2825 added an explicit CUDA graph replay handle for static prepared
fixed-radius ranked-summary aggregate batches. Goal2827 takes the next small
runtime step: keep the graph topology static, but update the device-resident
request buffers for a new same-shape `(radius, k_max)` sweep before replay.

This supports repeated RTNN-style parameter sweeps without rebuilding the CUDA
graph every time. The contract is still generic:

- prepared fixed-radius 3-D search handle;
- prepared query-points handle;
- unchanged request count;
- updated device arrays for radius and `k_max`;
- replay of the existing fused block-partial batch kernel.

No RTNN-specific native ABI or app-shaped native continuation is introduced.

## Implementation

Native OptiX adds:

- `rtdl_optix_update_fixed_radius_ranked_summary_aggregate_batch_graph_3d`

Python adds:

```python
graph = prepared.prepare_ranked_summary_prepared_queries_batch_graph(
    prepared_queries,
    requests_a,
    precision="float32",
)
rows_a = graph.replay()
graph.update_requests(requests_b)
rows_b = graph.replay()
```

The update path:

- requires the same request count as the original graph;
- revalidates radius and `k_max` against the prepared handle;
- uploads new compact radius and `k_max` arrays to the existing device buffers;
- does not rebuild or replace the captured graph;
- records `request_buffer_update_count` in replay result dictionaries.

## Pod Evidence

Pod:

- SSH command supplied by the user: `ssh root@69.30.85.171 -p 22167 -i ~/.ssh/id_ed25519`
- GPU: NVIDIA RTX A5000, driver 570.211.01
- Base source commit before applying the Goal2827 patch:
  `683352e9566e1663521f9f166318fc744162cb68`
- CUDA/OptiX setup: CUDA 12 build, OptiX SDK at `/root/vendor/optix-sdk`
- Artifact directory:
  `docs/reports/goal2827_rtnn_cuda_graph_request_update_pod/`

Probe:

- 32,768 deterministic 3-D search/query points;
- four request slots;
- direct fused-batch control for request set A;
- graph replay for request set A;
- direct fused-batch control for request set B;
- update existing graph handle to request set B;
- graph replay for request set B;
- 20 repeats comparing update+replay against rebuild-graph+replay.

| Points | Requests | Update+Replay Median (s) | Rebuild+Replay Median (s) | Rebuild / Update |
| ---: | ---: | ---: | ---: | ---: |
| 32,768 | 4 | 0.000373542 | 0.000396671 | 1.062x |

Correctness checks:

- direct fused-batch request set A matches graph replay set A;
- direct fused-batch request set B matches updated graph replay set B;
- `request_buffer_update_count_after_b == 1`;
- phase telemetry remains
  `prepared_query_uniform_cell_ranked_summary_aggregate_f32_batch_cuda_graph_replay`.

## Interpretation

This is a small but useful runtime hardening step. It removes graph rebuild
overhead for same-shape request sweeps while keeping the CUDA graph topology
stable and explicit.

The measured improvement is modest, about 1.06x against rebuilding the graph for
this 32K probe. That is expected: the graph rebuild cost is already small at
this scale. The design value is larger than the single timing number because it
gives repeated parameter sweeps a stable API and a clean validation boundary.

## Claim Boundary

This goal does not authorize:

- making graph replay the default path;
- public RTDL-beats-CuPy wording;
- public RTDL-beats-RTNN-paper wording;
- paper reproduction wording;
- whole-app speedup wording;
- broad RT-core speedup wording;
- v2.5 release wording.

The accepted claim is narrower: RTDL v2.5 now has an opt-in, same-shape request
buffer update path for the static prepared CUDA graph aggregate-batch handle,
with exact-parity pod evidence and a measured 1.062x update+replay advantage
over rebuilding the graph+replay in the recorded 32K RTX A5000 probe.

## Next Step

This completes the obvious graph-reuse slice. The next larger v2.5 step should
return to the partner-composition target: event-ordered chaining from
device-resident RT/aggregate outputs into partner consumers without a host
scalar synchronization boundary.

