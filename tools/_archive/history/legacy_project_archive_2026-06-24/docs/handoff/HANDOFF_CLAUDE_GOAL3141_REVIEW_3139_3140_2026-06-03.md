# Handoff: Claude Review for Goals3139 and 3140

Date: 2026-06-03

Please perform an independent read-only Claude review of the latest v2.8
partner-front-door fixes after Goal3138.

## Files To Review

Reports and artifacts:

- `docs/reports/goal3139_numba_kernel_cache_grouped_arg_perf_fix_2026-06-03.md`
- `docs/reports/goal3139_pod_artifacts/numba_kernel_cache_timing_2026-06-03.json`
- `docs/reports/goal3140_v2_8_canonical_schema_and_deferred_front_door_ops_2026-06-03.md`
- `docs/reports/goal3140_pod_artifacts/v2_8_canonical_schema_pod_smoke_2026-06-03.json`

Code and tests:

- `src/rtdsl/numba_partner_continuation.py`
- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `src/rtdsl/v2_8_typed_result_stream.py`
- `tests/goal3139_numba_kernel_cache_contract_test.py`
- `tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py`
- `scripts/goal3139_numba_kernel_cache_pod_probe.py`
- `scripts/goal3140_v2_8_canonical_schema_pod_smoke.py`

## Review Questions

1. Does Goal3139 correctly identify repeated Numba dispatcher construction as
   the main grouped-arg performance issue, based on the Goal3136/3139 timing
   delta?
2. Is the kernel cache implementation app-agnostic and safe for the current
   preview partner surface?
3. Does Goal3140 close the Goal3138 low debts for canonical ranked-summary pod
   evidence, `compact_mask_i64` rationale, and min/max deferral rationale?
4. Is the documented one-based `grouped_topk_f64` rank convention consistent
   with the reference and Torch implementation?
5. Are all release/speedup/zero-copy/hidden-dispatch/auto-partner/app-specific
   native-engine/user-shader-injection claim boundaries still intact?

## Required Output

Write the review to:

`docs/reviews/goal3141_claude_review_numba_cache_and_schema_closure_2026-06-03.md`

Use one of the standard verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please lead with findings by severity, then answer the five review questions.
Do not mutate source files unless you find a critical issue that cannot be
explained in the review alone.
