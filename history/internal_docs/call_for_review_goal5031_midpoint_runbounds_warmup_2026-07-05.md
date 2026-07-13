# Call For Review: Goal5031 Midpoint / Run-Bounds Warmup

Date: 2026-07-05

## Requested Verdict

`approve_goal5031_device_carrier_parity_candidate_pending_n_run_default_gate`

## Files Under Review

- `history/internal_docs/goal5031_midpoint_runbounds_warmup_result_2026-07-05.md`
- `history/internal_docs/rtdl_goal5031_query6_device_carrier_midpoint_runbounds_warmup_top4.json`
- `history/internal_docs/rtdl_goal5031_query6_cpu_carrier_current_control_top4.json`
- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`

## Review Questions

1. Does Goal5031 warm only tiny dummy kernels, without replaying real top4 query batches?
2. Did the implementation remain in app-layer warmup and avoid RTDL core/native changes?
3. Does the evidence show device-carrier first batch improved from Goal5030 `0.643663s` to `0.382333s`?
4. Does the device-carrier route now beat the contemporaneous CPU-carrier control but only match the older best CPU artifact?
5. Is it correct to classify the result as parity / candidate-default, rather than an immediate default switch?
6. Is the N-run default-decision matrix the correct next gate?
7. Does the report avoid cold CLI, paper-text, author-parity, zero-copy, and 10x claims?

## Non-Authorization Boundary

This review must not authorize:

- default switch without an N-run matrix;
- author-performance or 10x claims;
- cold CLI one-shot speedup;
- paper-text speedup;
- hidden RayJoin primitive promotion into RTDL core.
