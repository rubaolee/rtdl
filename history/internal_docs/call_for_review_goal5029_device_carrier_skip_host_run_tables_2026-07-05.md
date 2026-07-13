# Call For Review: Goal5029 Device-Carrier Skip Host Run Tables

Date: 2026-07-05

## Requested Verdict

`approve_goal5029_device_carrier_steady_state_win_first_batch_still_blocks_default`

## Files Under Review

- `history/internal_docs/goal5029_device_carrier_skip_host_run_tables_result_2026-07-05.md`
- `history/internal_docs/rtdl_goal5029_query6_device_carrier_skip_host_run_tables_top4.json`
- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal5021_prepared_lsi_base_session_test.py`

## Review Questions

1. Did Goal5029 remain app-layer only and avoid introducing a RayJoin-specific RTDL core/native primitive?
2. Is the `with_host_run_tables` change conservative, with default behavior preserved for CPU-carrier and validation routes?
3. Does the device-carrier route now explicitly skip host `run_start` / `run_end` tables while retaining host `order` / `edge_ids` for other app phases?
4. Does the artifact prove the skip occurred via `sort_map*_device_columnar_host_run_tables_skipped = 1.0`?
5. Are structural anchors stable across routes?
6. Does the evidence support a later-batch steady-state improvement (`0.694757s` later-batch sum vs CPU `0.832571s`)?
7. Does the first-batch cost (`1.628664s`) still block making device-carrier the default?
8. Does the report avoid cold CLI, paper-text, author-parity, broad zero-copy, and 10x claims?
9. Is the recommended next goal correct: device-carrier warmup / kernel precompile probe with first-batch and later-batch evidence?

## Non-Authorization Boundary

This review must not authorize:

- switching v2.14.3 default route to device-carrier;
- author-performance or 10x claims;
- cold CLI one-shot speedup claims;
- paper-text route speedup claims;
- claiming the route is fully zero-copy;
- promoting RayJoin app semantics into RTDL core.
