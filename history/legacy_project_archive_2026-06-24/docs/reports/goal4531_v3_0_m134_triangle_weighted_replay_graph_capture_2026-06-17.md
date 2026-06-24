# Goal4531 / V3 M134 Triangle Weighted Replay Graph Capture

## Conclusion

M134 validates a generic prepared ray-batch weighted-summary device-output executor on a caller stream, removing the host scalar read from that replay path. CUDA graph capture of the OptiX weighted launch is fail-closed on this pod with a captured CUDA/OptiX error, so the future Triangle M113 graph shape remains blocked while the current large-row Triangle route remains Goal4479/Goal4511.

## Runtime

- Expected weighted sum: `20`
- Host-scalar baseline: `20`
- Device-output stream launch: `20`
- Device-output stream validated: `True`
- Graph capture validated: `False`
- Graph replay sums: `[]`
- Graph capture error: `RuntimeError: OptiX error: CUDA error`

## M113 Gate

- Ready for M113 plan: `False`
- Blockers: `prepared_graph_capture_not_validated`
- Chunk count: `0`

## Boundary

- No current Triangle Counting route changed.
- No app-specific native callback was introduced.
- No automatic partner selection, public speedup, or RT-core speedup wording is authorized.
