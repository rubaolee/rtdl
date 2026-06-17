# Goal4505 / V3 M109 RTNN Partner-Continuation Chunk Plan

## Conclusion

The RTNN same-stream partner-continuation route now has an explicit front-door chunk plan. A 1,048,576-query partner-continuation workload is planned as 16 chunks of at most 65,536 queries, reusing the prepared scene but preparing query points, a CUDA graph, and the same-stream partner reduction per chunk. This is planner evidence only; large chunked runtime evidence remains required before performance wording.

## Plan Matrix

| Scenario | Query count | Chunk count | Status | Runtime executed |
| --- | ---: | ---: | --- | --- |
| single graph | 65,536 | 1 | `single_graph_partner_continuation` | false |
| large partner continuation | 1,048,576 | 16 | `chunked_partner_continuation_required` | false |

## Large Chunk Contract

- First chunk: `{'chunk_index': 0, 'query_offset': 0, 'query_start_inclusive': 0, 'query_end_exclusive': 65536, 'query_count': 65536, 'prepared_scene_reused': True, 'prepared_query_points_per_chunk': True, 'cuda_graph_per_chunk': True, 'same_stream_partner_device_reduction_per_chunk': True, 'host_materialization_before_partner': False}`.
- Last chunk: `{'chunk_index': 15, 'query_offset': 983040, 'query_start_inclusive': 983040, 'query_end_exclusive': 1048576, 'query_count': 65536, 'prepared_scene_reused': True, 'prepared_query_points_per_chunk': True, 'cuda_graph_per_chunk': True, 'same_stream_partner_device_reduction_per_chunk': True, 'host_materialization_before_partner': False}`.
- Prepared scene reuse is required across chunks.
- Prepared query points, CUDA graph capture, and same-stream partner reduction are per chunk.
- Host materialization before the partner is blocked.
- Full-batch aggregate-only direct mode is not a substitute for partner continuation.

## Boundary

- This packet is planner evidence only.
- It does not execute the chunked runtime path.
- It does not authorize automatic dispatch, automatic partner selection, public speedup wording, or RT-core speedup wording.
