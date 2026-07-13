# Call For Review - Goal5160 Active Frontier Rows

Please strictly review Goal5160.

## Files

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/partner_continuations.py`
- `Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py`
- `tests/goal5148_native_3d_cell_mbr_frontier_test.py`
- `tests/goal5159_row_table_only_frontier_route_test.py`
- `tests/goal5160_active_frontier_rows_test.py`
- `Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_active_frontier_profile_pod.json`
- `Paper-reproduction-apps/x-hd-paper/data/manifest.json`
- `history/internal_docs/goal5160_active_frontier_rows_result_2026-07-08.md`

## Review Questions

1. Is `emit_pruned_rows` a generic native frontier-row emission option rather
   than an X-HD-specific shortcut?
2. Is backward compatibility preserved by keeping `emit_pruned_rows=True` as
   the default?
3. Does the native any-hit path avoid atomic append/copy/sort work for pruned
   rows only when `emit_pruned_rows=false`?
4. Is it semantically safe for the X-HD streaming route to set
   `emit_pruned_rows=false`, given that the continuation already ignores pruned
   rows?
5. Does the POD artifact show author HDResult matching, `validation_mode=author-only`,
   and no speedup/parity ratio?
6. Is the before/after comparison against Goal5159 fair as an RTDL-route
   comparison, while avoiding author parity/speedup claims?
7. Is the interpretation correct that row volume dropped substantially and that
   seed is now the next measured route target?
8. Does the manifest entry avoid overstating this as full paper reproduction,
   author algorithm equivalence, or denominator-aligned paper performance?

## Expected Verdict Shape

```text
verdict_label:
blocking_findings:
required_amendments:
non_blocking_notes:
```
