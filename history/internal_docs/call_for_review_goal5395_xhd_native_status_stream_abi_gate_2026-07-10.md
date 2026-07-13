# Call For Review: Goal5395 X-HD Native Status-Stream ABI Gate

Date: 2026-07-10

Please strictly review Goal5395.

## Files Under Review

```text
src/rtdsl/active_query_status.py
src/rtdsl/__init__.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5395_native_status_stream_abi_gate.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5395_native_status_stream_abi_gate.json
tests/goal5395_native_status_stream_abi_gate_test.py
history/internal_docs/goal5395_xhd_native_status_stream_abi_gate_result_2026-07-10.md
```

Context files:

```text
history/internal_docs/goal5394_xhd_full_cover_delta_status_probe_result_2026-07-10.md
history/internal_docs/call_for_review_goal5394_xhd_full_cover_delta_status_probe_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5394_full_cover_delta_status_probe.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json
src/native/optix/rtdl_optix_prelude.h
src/native/optix/rtdl_optix_api.cpp
src/rtdsl/optix_runtime.py
```

## Review Questions

1. Does Goal5395 add an app-neutral public RTDL ABI contract for a future native
   active-query status stream, rather than an X-HD-specific primitive?
2. Are the exported constants/functions appropriate:
   `ACTIVE_QUERY_STATUS_STREAM_NATIVE_ABI_CONTRACT`,
   `ACTIVE_QUERY_STATUS_STREAM_NATIVE_ROW_SCHEMA`,
   `ACTIVE_QUERY_STATUS_STREAM_NATIVE_TELEMETRY_SCHEMA`,
   `active_query_status_stream_native_abi_contract()`, and
   `validate_active_query_status_stream_native_abi_contract()`?
3. Is the required row schema sufficient for the Goal5394 target, especially
   `active_queue_index`, `source_id`, `status_code`,
   `transition_phase_code`, `current_best_before_sq`, and
   `current_best_after_sq`?
4. Is the required telemetry schema sufficient to prevent a row-count-only
   shortcut, especially hash/sample rows, offloading status count, feedback
   update count, miss/completed/aborted counts, and raw rows before sort/reduce?
5. Does the artifact correctly carry forward the Goal5394 target:
   author `27,133,990 = 62 * active_count`, full-cover
   `24,508,120 = 56 * active_count`, missing `2,625,870 = 6 * active_count`,
   while keeping `full_cover_is_correctness_claim = false`?
6. Does the current native surface audit correctly show that
   `rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v6` exists but is
   insufficient because it is a single-launch frontier probe rather than a
   multi-round active-query status stream?
7. Is it correct that the future symbol
   `rtdl_optix_collect_active_query_status_stream_3d_v1` is not yet present and
   no native backend was implemented in Goal5395?
8. Do the tests adequately enforce app-neutrality and prevent accidental X-HD /
   paper / figure / author-entrypoint wording in the core contract?
9. Does Goal5395 preserve the claim boundary: no explicit `-lb`, no row/hash
   parity, no Figure 7/11 reproduction, no same-denominator memory, no
   performance ratio, no exact paper dataset reproduction, and no full X-HD
   paper reproduction?
10. Should the next goal implement a generic native v7 active-query status-stream
    backend, or fail-close explicit load-balance support if that would require
    X-HD-specific constants or author-only status logic?

## Requested Verdict Labels

Approve:

```text
approve_goal5395_native_status_stream_abi_gate
```

Approve with amendments:

```text
approve_with_required_amendments_goal5395_native_status_stream_abi_gate
```

Block:

```text
block_goal5395_native_status_stream_abi_gate_overclaims_or_app_specific
```

## Expected Answer Shape

Please answer with:

```text
Verdict:

Blocking findings:

Required amendments:

Non-blocking notes:

Answers to the 10 review questions:
```
