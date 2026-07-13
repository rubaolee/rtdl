# Call For Review: Goal5028 Device-Carrier Prepared Arrays Probe

Date: 2026-07-05

## Requested Verdict

`approve_goal5028_device_carrier_prepared_arrays_small_steady_state_win_keep_default_cpu_carrier`

## Files Under Review

- `history/internal_docs/goal5028_device_carrier_prepared_arrays_probe_result_2026-07-05.md`
- `history/internal_docs/rtdl_goal5028_query6_device_carrier_prepared_arrays_top4.json`
- `history/internal_docs/rtdl_goal5028_query6_device_resident_carrier_probe_top4.json`
- `history/internal_docs/rtdl_goal5027_query6_sort_reuse_prepared_segments_repeat_control_top4.json`
- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal5021_prepared_lsi_base_session_test.py`

## Review Questions

1. Did Goal5028 remain in app-layer code and avoid adding any RayJoin-specific RTDL core/native primitive?
2. Did the change genuinely remove repeated per-batch carrier dataset copies in the device-resident carrier route?
3. Are the structural anchors stable across the CPU-carrier and device-carrier routes (`428322` total LSI rows, first-batch `127926` LSI rows, first-batch descriptor pair count `6316`)?
4. Does the evidence support a small later-batch steady-state win for prepared device carrier (`0.797362s` later-batch sum vs CPU carrier `0.832571s`)?
5. Does the first-batch device-carrier cost (`1.741995s`) still block making device carrier the default v2.14.3 route?
6. Is it correct to keep CPU carrier as the default while retaining device carrier behind an explicit experimental/prepared-regime flag?
7. Does the report avoid cold CLI, paper-text, author-parity, broad 10x, or warm-only headline claims?
8. Is the recommended next step correct: either attack first-call device-carrier/JIT cost or skip unused host run-table work, but only with first/later-batch matrices?

## Non-Authorization Boundary

This review must not authorize:

- author-performance parity;
- paper-text route speedups;
- cold CLI one-shot speedups;
- a v2.14.3 default switch to device carrier;
- a hidden RayJoin core primitive;
- broad device-resident or zero-copy claims beyond the measured route.
