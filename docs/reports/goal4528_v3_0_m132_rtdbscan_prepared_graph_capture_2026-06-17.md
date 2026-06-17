# Goal4528 / V3 M132 RT-DBSCAN Prepared Graph Capture

## Conclusion

M132 validates the missing RT-DBSCAN prepared graph-capture gate: chunk-local predicate direct-status handles can capture a fixed-iteration CuPy CUDA graph, replay it twice, and match the same prepared handle's non-graph fixed-iteration output without coordinate upload, host pre-partner materialization, pair-row materialization, or app-specific native ABI. This authorizes the internal M113 plan shape for RT-DBSCAN, not public speedup wording or automatic partner selection.

## Runtime

- Runtime executed: `True`
- Partner: `cupy`
- Chunk count: `2`
- Fixed iteration count: `1`

## Chunk Capture

| Chunk | Captured | Replays | Matches normal | Upload avoided | Pair rows avoided |
| --- | --- | ---: | --- | --- | --- |
| `0:6` | `True` | 2 | `True` | `True` | `True` |
| `6:12` | `True` | 2 | `True` | `True` | `True` |

## Readiness

- Ready for M113 plan: `True`
- Plan status: `chunked_partner_continuation_required`
- Chunk count: `31`

## Boundary

- This is internal CUDA graph-capture readiness evidence.
- No current RT-DBSCAN route changed.
- No public speedup, RT-core speedup, or automatic partner-selection wording is authorized.
