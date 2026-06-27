# Goal4516 / V3 M120 Prepared Graph Chunk Adoption Gate

## Conclusion

M120 turns M113 from a single RTNN-derived plan into a reusable adoption gate. RTNN is ready for M113 planning; RT-DBSCAN, Triangle Counting, Spatial RayJoin, and Barnes-Hut remain blocked for distinct runtime reasons. This is a core/runtime safety gate, not automatic dispatch or new performance evidence.

## Adoption Matrix

| Scenario | Ready | Plan chunks | Blockers | Reader action |
| --- | --- | ---: | --- | --- |
| RTNN M19/M113 chunked graph partner bridge | `True` | 16 | none | Use M113 planning for explicit same-stream partner partials. |
| RT-DBSCAN future compact-status graph continuation | `False` | 0 | missing_prepared_item_handle_per_chunk, prepared_graph_capture_not_validated | Do not promote M113 as the RT-DBSCAN route until a chunk-local direct-status handle and validated graph capture exist. |
| Triangle prepared replay with unique-count continuation | `False` | 0 | missing_prepared_item_handle_per_chunk, prepared_graph_capture_not_validated, partner_continuation_not_associative | Keep the current direct sort/RLE path; use M113 discipline only after chunk-boundary duplicate handling is proven associative. |
| Spatial RayJoin repeated PIP graph replay | `False` | 0 | missing_explicit_partner_continuation, prepared_graph_capture_not_validated | Use the prepared batch executor; Goal4451 quarantines prepared-points CUDA graph replay. |
| Barnes-Hut aggregate-frontier row route | `False` | 0 | missing_prepared_scene_reuse, missing_prepared_item_handle_per_chunk, prepared_graph_capture_not_validated, host_materialization_before_partner | Do not force M113 onto the frontier-row route; implement the future generic fused weighted-vector primitive instead. |

## Boundary

- This gate does not execute runtime work.
- It does not authorize public speedup wording.
- It does not authorize automatic partner selection or hidden dispatch.
- A blocked app must remove every listed blocker before using M113 as a promoted route.
