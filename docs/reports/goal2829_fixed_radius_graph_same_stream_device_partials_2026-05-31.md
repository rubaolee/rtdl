# Goal2829 Fixed-Radius Graph Same-Stream Device Partials

Date: 2026-05-31

## Purpose

Goal2829 closes the next v2.5 partner-composition slice after Goal2827. The prepared fixed-radius aggregate CUDA graph already amortized launch overhead and supported same-shape request-buffer updates, but its public replay path still synchronized the producer stream, downloaded native partial rows, and reduced them on the host.

This goal adds a separate opt-in path that launches the prepared CUDA graph and exposes its device-resident partial aggregate rows plus the native CUDA stream pointer. Python then runs a bounded CuPy rawkernel consumer on that same CUDA stream, reducing the partial rows before any producer-side host scalar read or host partial-row materialization.

## Implementation

- Native OptiX ABI added:
  - `rtdl_optix_launch_fixed_radius_ranked_summary_aggregate_batch_graph_device_partials_3d`
- Native implementation added:
  - `launch_fixed_radius_ranked_summary_aggregate_batch_graph_device_partials_3d_optix(...)`
- The native path:
  - calls `cuGraphLaunch(graph_exec, stream)`;
  - returns the device pointer for the graph-owned `RtdlFixedRadiusRankedNeighborAggregate` partial rows;
  - returns `partial_count`, `request_count`, `query_block_count`, and the native CUDA stream pointer;
  - deliberately does not call `cuStreamSynchronize`;
  - deliberately does not download partial rows.
- Python API added:
  - `PreparedOptixFixedRadiusRankedSummaryAggregateBatchGraph3D.replay_same_stream_device_partials_summary_cupy()`
- Python consumer added:
  - `_run_fixed_radius_graph_partials_same_stream_summary_cupy(...)`
  - wraps the native partial pointer through `cupy.cuda.UnownedMemory`;
  - wraps the native stream through `cupy.cuda.ExternalStream`;
  - launches `rtdl_fixed_radius_graph_partials_same_stream_summary` after the producer graph launch on the same stream;
  - returns the same aggregate schema as `replay()` after the bounded consumer synchronizes for final materialization.

The ordinary `graph.replay()` behavior is unchanged and remains the host-reduced compatibility path.

## Contract Metadata

The same-stream path reports:

- `producer_consumer_stream_ordering: same_cuda_stream`
- `producer_host_synchronization_used: false`
- `host_scalar_read_before_consumer: false`
- `host_partial_materialization_before_consumer: false`
- `device_resident_partial_rows_for_partner: true`
- `bounded_partner_consumer: cupy_rawkernel`
- `async_partner_continuation_authorized: true`
- `async_partner_continuation_authorization_scope: bounded_same_stream_fixed_radius_graph_partial_summary_consumer_only`
- `general_partner_continuation_authorized: false`
- `true_zero_copy_authorized: false`
- `public_speedup_claim_authorized: false`

## Pod Validation

Pod: `root@69.30.85.171:22167`

Build:

```text
make build-optix CUDA_PREFIX=/usr/local/cuda-12 OPTIX_PREFIX=/root/vendor/optix-sdk
```

Result: build passed.

Focused tests:

```text
python3 -m unittest \
  tests.goal2829_fixed_radius_graph_same_stream_device_partials_test \
  tests.goal2827_rtnn_cuda_graph_request_update_test \
  tests.goal2825_rtnn_cuda_graph_replay_prepared_batch_test
```

Result:

```text
Ran 13 tests in 0.016s
OK
```

Runtime smoke artifact:

- `docs/reports/goal2829_fixed_radius_graph_same_stream_device_partials_pod/goal2829_summary.json`

Runtime smoke summary:

- point count: 4096
- request count: 4
- direct `graph.replay()` matched `graph.replay_same_stream_device_partials_summary_cupy()` for:
  - `query_count`
  - `bounded_neighbor_count`
  - `nearest_id_checksum`
  - `kth_id_checksum`
  - `sum_distance`
- mismatch count: 0

The pod smoke validates the narrow contract: a bounded CuPy partner consumer can reduce the graph partial rows on the same native CUDA stream and match the existing host-reduced replay output.

## Claim Boundary

`accept-with-boundary`

This proves one bounded CuPy consumer can reduce device-resident fixed-radius graph partial rows on the same native CUDA stream without a producer-side host scalar sync.

This does not authorize broad true-zero-copy, arbitrary partner continuation, public RTDL-beats-CuPy, public RTDL-beats-RTNN-paper, whole-app speedup, broad RT-core speedup, paper reproduction, or v2.5 release claims.

This goal does not make graph replay, CUDA graph update, or same-stream CuPy consumption the default runtime path. The new path is explicit and opt-in.

## Next Step

The next v2.5 step should generalize this proof from a fixed aggregate summary consumer into a richer typed primitive-payload column handoff. The key remaining design question is how to publish typed payload column descriptors and lifetime ownership in a partner-neutral way without falling back into torch-specific coercion or app-shaped adapter APIs.
