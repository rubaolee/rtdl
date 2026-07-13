# Call For Review: Goal5032 N-Run Default Decision Matrix

Date: 2026-07-05

## Requested Verdict

`approve_goal5032_cpu_default_device_steady_state_win_only`

## Files Under Review

- `history/internal_docs/goal5032_nrun_default_decision_matrix_result_2026-07-05.md`
- `history/internal_docs/rtdl_goal5032_nrun_cpu_1_top4.json`
- `history/internal_docs/rtdl_goal5032_nrun_cpu_2_top4.json`
- `history/internal_docs/rtdl_goal5032_nrun_cpu_3_top4.json`
- `history/internal_docs/rtdl_goal5032_nrun_device_1_top4.json`
- `history/internal_docs/rtdl_goal5032_nrun_device_2_top4.json`
- `history/internal_docs/rtdl_goal5032_nrun_device_3_top4.json`

## Review Questions

1. Is this N-run matrix the right gate before any device-carrier default switch?
2. Are the CPU and device routes measured under the same top4, same code, same prepared LSI base-session query-batch regime?
3. Are structural anchors stable across all runs?
4. Does the evidence support keeping CPU carrier as default (`0.971880s` median six-batch sum vs device `1.063056s`)?
5. Does the evidence also support that device-carrier is genuinely better in later batches (`0.663246s` vs CPU `0.771825s`)?
6. Is the report correct to classify device-carrier as steady-state-only win, not default route?
7. Does the report avoid cold CLI, paper-text, author-parity, zero-copy, and 10x claims?
8. Is the recommended next decision correct: stop v2.14.3 here or continue only with a first-batch-focused N-run gate?

## Non-Authorization Boundary

This review must not authorize:

- switching v2.14.3 default route to device carrier;
- author-performance parity;
- cold CLI one-shot speedups;
- paper-text speedups;
- 10x claims;
- hidden RayJoin semantics in RTDL core.
