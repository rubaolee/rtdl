# External Review Handoff: Goals3718-3719 RayJoin LSI Native Repeated Diagnostic

Please perform a read-only independent review of the Goal3718/Goal3719 RayJoin LSI diagnostic chain.

## Files To Inspect

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal3718_rayjoin_lsi_native_repeated_count_diagnostic.py`
- `tests/goal3718_segment_pair_prepared_left_repeated_count_diagnostic_test.py`
- `docs/reports/goal3718_segment_pair_prepared_left_repeated_count_a5000/summary.json`
- `docs/reports/goal3719_rayjoin_lsi_native_repeated_count_diagnostic_pod_validation_2026-06-07.md`
- `tests/goal3719_rayjoin_lsi_native_repeated_count_diagnostic_pod_validation_test.py`

## Questions

1. Does the native repeated-count ABI preserve the existing generic segment-pair exact-count semantics without introducing RayJoin/app-specific native logic?
2. Does the pod artifact support the conclusion that Python/ctypes overhead is not the material source of the remaining RayJoin LSI gap?
3. Are the claim boundaries correct, especially the refusal to claim RTDL beats RayJoin, paper reproduction, release readiness, RT-core speedup, or true zero-copy?
4. Is the next engineering target correctly identified as native OptiX route mechanics rather than Python adapter work?
5. Are there any correctness, benchmark fairness, or methodology defects that should block using this diagnostic to guide the next optimization goal?

## Expected Output

Write one review file:

- Gemini: `docs/reviews/goal3720_gemini_review_goal3718_3719_rayjoin_lsi_native_repeated_diagnostic_2026-06-07.md`
- Claude: `docs/reviews/goal3721_claude_review_goal3718_3719_rayjoin_lsi_native_repeated_diagnostic_2026-06-07.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

This is a review task only. Do not edit source files, reports, scripts, tests, or pod artifacts other than the requested review file.
