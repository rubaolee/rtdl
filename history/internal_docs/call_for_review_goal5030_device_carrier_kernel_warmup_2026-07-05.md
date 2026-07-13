# Call For Review: Goal5030 Device-Carrier Kernel Warmup

Date: 2026-07-05

## Requested Verdict

`approve_goal5030_device_carrier_first_batch_reduced_default_still_cpu_carrier`

## Files Under Review

- `history/internal_docs/goal5030_device_carrier_kernel_warmup_result_2026-07-05.md`
- `history/internal_docs/rtdl_goal5030_query6_device_carrier_kernel_warmup_top4.json`
- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`

## Review Questions

1. Does the new warmup use tiny dummy arrays rather than replaying real top4 query rows?
2. Did the implementation remain in the app-layer warmup path and avoid RTDL core/native changes?
3. Does the result support that first-batch device-carrier cost dropped from `1.628664s` to `0.643663s`?
4. Does the six-batch device-carrier route still lose to CPU carrier (`1.318018s` vs `1.034264s`), blocking a default switch?
5. Is the later-batch steady-state win real but correctly scoped (`0.674355s` vs CPU `0.832571s`)?
6. Does the report correctly identify remaining first-batch costs in midpoint device-query, device run-bound generation, descriptor consumer, and carrier construction?
7. Does the report avoid cold CLI, paper-text, author-parity, broad zero-copy, and 10x claims?
8. Is it correct to continue focused first-batch warmup work while keeping CPU carrier as default?

## Non-Authorization Boundary

This review must not authorize:

- v2.14.3 default switch to device-carrier;
- author-performance parity;
- cold CLI one-shot speedup;
- paper-text route speedup;
- 10x claims;
- hidden RayJoin primitive promotion into RTDL core.
