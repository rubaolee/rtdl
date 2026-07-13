# Call For Review - Goal5159 Row-Table-Only Native Frontier Route

Please strictly review Goal5159.

## Files

- `src/rtdsl/partner_continuations.py`
- `Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py`
- `tests/goal5148_native_3d_cell_mbr_frontier_test.py`
- `tests/goal5159_row_table_only_frontier_route_test.py`
- `Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_row_table_only_frontier_profile_pod.json`
- `Paper-reproduction-apps/x-hd-paper/data/manifest.json`
- `history/internal_docs/goal5159_row_table_only_frontier_route_result_2026-07-08.md`

## Review Questions

1. Does `return_split_frontiers=False` preserve the generic row-table contract
   while avoiding unnecessary split-frontier materialization for streaming
   consumers?
2. Is backward compatibility preserved by keeping `return_split_frontiers=True`
   as the default?
3. Does the X-HD route use row-table-only mode only because it consumes
   `frontier["row_table"]`, without adding X-HD-specific semantics to RTDL core?
4. Does metadata truthfully expose whether split frontiers were returned?
5. Does the POD artifact show author HDResult matching and
   `validation_mode=author-only`, with no exact-reference validation in
   production-style timing?
6. Is the before/after comparison against Goal5158 fair as an RTDL-route
   comparison, while avoiding author parity/speedup claims?
7. Is the interpretation correct that the improvement is modest and that the
   remaining frontier cost is mostly native row volume/production rather than
   split-frontier materialization?
8. Does the manifest entry avoid overstating this as full paper reproduction,
   author algorithm equivalence, or denominator-aligned paper performance?

## Expected Verdict Shape

```text
verdict_label:
blocking_findings:
required_amendments:
non_blocking_notes:
```
