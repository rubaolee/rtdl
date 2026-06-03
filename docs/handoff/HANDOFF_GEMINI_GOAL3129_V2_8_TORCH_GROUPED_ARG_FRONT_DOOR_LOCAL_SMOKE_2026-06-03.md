# Handoff: Gemini Review For Goal3129 v2.8 Torch Grouped-Arg Front Door Local Smoke

Please review Goal3129 and write the review to:

`docs/reviews/goal3130_gemini_review_goal3129_torch_grouped_arg_front_door_local_smoke_2026-06-03.md`

## Scope

Goal3129 records local Linux Torch functional smoke for the remaining v2.8
explicit partner-consumer front-door grouped-arg operations:

- `grouped_argmin_f64`
- `grouped_argmax_f64`

Both matched the Goal3114 Python reference consumer and kept claim flags false.

Goal3129 also summarizes the current local functional coverage table for all
currently supported v2.8 front-door operations, while preserving the Goal3126
Numba-specific local-host boundary.

## Files To Inspect

- `docs/reports/goal3129_v2_8_torch_grouped_arg_front_door_local_smoke_2026-06-03.md`
- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `docs/reports/goal3128_v2_8_torch_partner_front_door_and_numba_boundary_2ai_consensus_2026-06-03.md`

## Review Questions

1. Does the Torch smoke substantiate local functional parity for
   `grouped_argmin_f64` and `grouped_argmax_f64`?
2. Is the coverage table accurate and bounded?
3. Is it correct to keep Numba-specific validation open despite Torch grouped
   argmin/argmax passing?
4. Are the claim boundaries correct?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. Include findings by severity, claim boundary, files inspected, and
next step.
