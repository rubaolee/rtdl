# Handoff: Gemini Review for Goal3006-Goal3008 Numba Grouped Witness Path

## Requested Output

Write an independent Gemini review to:

`docs/reviews/goal3009_gemini_review_goal3006_3008_numba_grouped_witness_2026-06-01.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Scope

Review current `main` around:

- `src/rtdsl/numba_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/v2_6_roadmap.py`
- `scripts/goal3007_numba_grouped_arg_reducer_pod_runner.py`
- `docs/reports/goal3006_numba_grouped_argmin_argmax_preview_2026-06-01.md`
- `docs/reports/goal3007_numba_grouped_arg_reducer_pod_runner_2026-06-01.md`
- `docs/reports/goal3007_numba_grouped_arg_reducer_l4_pod_2026-06-01.md`
- `docs/reports/goal3007_numba_grouped_arg_reducer_l4_pod_2026-06-01.json`
- `docs/reports/goal3008_numba_group_argmin_global_argmax_front_door_2026-06-01.md`
- `tests/goal3006_numba_grouped_argmin_argmax_preview_test.py`
- `tests/goal3007_numba_grouped_arg_reducer_pod_runner_test.py`
- `tests/goal3007_numba_grouped_arg_reducer_l4_pod_test.py`
- `tests/goal3008_numba_group_argmin_global_argmax_front_door_test.py`

## Questions To Answer

1. Are `grouped_argmin_f64` and `grouped_argmax_f64` implemented as generic Numba partner continuations without app-specific native-engine logic?
2. Does the Goal3007 L4 artifact credibly validate equal-score ties, missing groups, dense outputs, compact outputs, and public adapter use from a clean source commit?
3. Does `group_argmin_then_global_argmax_partner_columns(..., partner="numba")` correctly compose the two generic operations for Hausdorff/RTNN-style witness selection without embedding app semantics?
4. Does the work preserve the user-choice rule for partners and avoid automatic partner selection?
5. Does any report, artifact, or metadata overclaim v2.6 release readiness, Numba speedup, RT-core speedup, whole-app speedup, true zero-copy, or app-specific engine behavior?
6. What risks remain before using this path as a recommended benchmark-app implementation?

## Validation Command

If shell execution is available, run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3008_numba_group_argmin_global_argmax_front_door_test tests.goal3007_numba_grouped_arg_reducer_l4_pod_test tests.goal3007_numba_grouped_arg_reducer_pod_runner_test tests.goal3006_numba_grouped_argmin_argmax_preview_test tests.goal3005_v2_6_numba_partner_progress_after_rayjoin_test
```

If shell execution is unavailable, disclose that clearly and perform a static/artifact review.

## Required Boundary

Do not authorize v2.6 release, public speedup wording, Numba speedup wording, broad RT-core speedup wording, whole-app speedup wording, true-zero-copy wording, automatic partner selection, app-specific native-engine logic, or benchmark paper reproduction claims.
