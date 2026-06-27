# Goal4530 / V3 M133 Triangle Device Key-Payload Merge

## Conclusion

M133 validates the app-agnostic device-side key/count payload merge needed by Triangle Counting when duplicate logical keys cross chunk boundaries. This removes the key-payload final-merge debt, but the current Triangle M113 gate remains blocked on prepared graph capture for the weighted prepared replay path.

## Device Merge

- Runtime executed: `True`
- Partner: `cupy`
- Unique keys: `[11, 17, 23, 29, 31, 37]`
- Counts: `[6, 5, 5, 1, 1, 1]`
- Total weight: `19`
- Cross-chunk duplicate delta: `3`
- Host key materialization before merge: `False`

## M113 Gate

- Current Triangle ready: `False`
- Current blockers: `prepared_graph_capture_not_validated`
- Future gate with graph capture: `True`

## Boundary

- No current Triangle Counting route changed.
- No app-specific native callback was introduced.
- No automatic partner selection, public speedup, or RT-core speedup wording is authorized.
