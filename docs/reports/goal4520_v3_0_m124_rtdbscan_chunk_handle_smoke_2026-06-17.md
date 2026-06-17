# Goal4520 / V3 M124 RT-DBSCAN Chunk-Handle Smoke

## Conclusion

M124 validates the RT-DBSCAN live chunk-handle smoke that M123 left open: caller-owned CuPy point-column slices can be prepared as chunk-local predicate direct-status handles and replayed without coordinate upload or pair-row materialization. M113 promotion remains blocked because prepared graph capture is still not validated.

## Runtime

- Runtime executed: `True`
- Partner: `cupy`
- Chunk count: `2`
- Base point count: `12`

## Chunk Smoke

| Chunk | Points | Runs | Upload avoided | Pointer offset | Label counts |
| --- | ---: | ---: | --- | ---: | --- |
| `0:6` | 6 | 2 | `True` | 0 | `3` |
| `6:12` | 6 | 2 | `True` | 48 | `3` |

## Readiness

- API shape ready: `True`
- Live chunk-handle smoke validated: `True`
- Ready for M113 plan: `False`
- Remaining blockers: `prepared_graph_capture_not_validated`

## Boundary

- This is CuPy runtime handle evidence, not RT-core speedup evidence.
- No current RT-DBSCAN route changed.
- M113 promotion remains blocked until prepared graph capture is validated.
- Automatic partner selection and public speedup wording remain blocked.
