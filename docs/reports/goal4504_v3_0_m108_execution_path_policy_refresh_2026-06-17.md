# Goal4504 / V3 M108 Execution-Path Policy Refresh

## Conclusion

The fixed-radius aggregate execution-path policy is now size-aware. Unknown or small aggregate-only OptiX work keeps the Goal2841 direct graph recommendation; explicit large aggregate-only work above 65,536 queries uses the Goal4502 full-batch prepared direct aggregate recommendation; partner continuations keep the same-stream graph/device-partial route with an explicit large-workload chunking warning.

## Scenario Matrix

| Scenario | Selected path | Recommended result mode | Evidence | Warning |
| --- | --- | --- | --- | --- |
| unknown_or_small_aggregate_only | direct_native_graph_replay | `ranked-summary-aggregate-prepared-query-batch-graph-float32` | Goal2841 | none |
| large_aggregate_only_kitti_1m | prepared_full_batch_direct_aggregate | `ranked-summary-aggregate-prepared-query-batch-float32` | Goal4502 | none |
| large_partner_continuation | same_stream_partner_continuation | `ranked-summary-aggregate-prepared-query-batch-graph-same-stream-cupy-float32` | Goal2841 | The current graph/device-partial partner-continuation path is sized around the 65,536-query graph cap; large partner-continuation workloads need explicit chunking or future large-partial evidence. |
| embree_backend | no_optix_graph_policy | `backend_specific_policy_required` | Goal2841 | Use explicit backend-specific measurement before selecting this path. |

## Boundary

- This is explain-only policy, not hidden runtime dispatch.
- Users and benchmark apps still choose explicit result modes.
- Public speedup wording and release-readiness wording remain blocked by this packet.
- Goal4502 supersedes Goal2841 only for explicit large aggregate-only batches; it does not replace the same-stream partner-continuation route.
