# Goal4521 / V3 M125 Triangle Unique-Count Gate

## Conclusion

M125 explains the Triangle Counting M113 blocker in app-agnostic terms. Per-chunk scalar unique counts are not associative when the same key can appear in more than one chunk. The generic fix is not an app-specific OptiX callback: carry key/count payloads to a final associative merge, or prove disjoint chunk key ranges. The current Triangle route remains blocked for M113 because graph capture and key-payload final merge are not both validated.

## Counterexample

- Scalar chunk sum: `5`
- Global unique count: `4`
- Scalar sum matches global unique: `False`
- Key-payload associative merge validated: `True`

## Triangle Current Gate

- Ready for M113 plan: `False`
- Blockers: `prepared_graph_capture_not_validated, missing_key_count_payload, chunk_boundary_duplicate_handling_not_associative`

## Generic Future Gate

- Ready for M113 plan with key payload and graph capture: `True`
- Plan status: `chunked_partner_continuation_required`
- Chunk count: `3`

## Boundary

- No runtime was executed.
- No current Triangle Counting route changed.
- The fix remains app-agnostic: key/count payload merge or disjoint key ranges.
- No app-specific native callbacks, automatic partner selection, public speedup, or RT-core speedup wording is authorized.
