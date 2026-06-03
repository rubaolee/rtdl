# Handoff: Claude Review Debt For v2.8 Goals3108-3131

Please perform an independent Claude review of the v2.8 work from Goal3108
through Goal3131 and write the review to:

`docs/reviews/goal3133_claude_review_v2_8_partner_front_door_chain_3108_3131_2026-06-03.md`

## Scope

Review the already-pushed v2.8 chain ending at commit `2809a45b`:

- Goal3108: typed result-stream contract
- Goal3111: segmented row stream to typed-stream adapter
- Goal3114: reference grouped-continuation consumer
- Goal3117: explicit partner-consumer front door
- Goal3120/3122: local Linux CuPy smoke and consensus
- Goal3123/3125: named output hardening and consensus
- Goal3126/3128: Torch top-k/bounded-collect smoke, bounded-collect canonical
  output filtering, Numba local boundary, and consensus
- Goal3129/3131: Torch grouped argmin/argmax local smoke and consensus

## Files To Inspect

- `src/rtdsl/v2_8_typed_result_stream.py`
- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `tests/goal3108_v2_8_typed_result_stream_contract_test.py`
- `tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py`
- `docs/reports/goal3108_v2_8_typed_result_stream_contract_2026-06-03.md`
- `docs/reports/goal3111_v2_8_segmented_typed_stream_adapter_2026-06-03.md`
- `docs/reports/goal3114_v2_8_reference_grouped_continuation_consumer_2026-06-03.md`
- `docs/reports/goal3117_v2_8_explicit_partner_consumer_front_door_2026-06-03.md`
- `docs/reports/goal3122_v2_8_cupy_partner_consumer_local_linux_smoke_2ai_consensus_2026-06-03.md`
- `docs/reports/goal3125_v2_8_partner_consumer_named_output_hardening_2ai_consensus_2026-06-03.md`
- `docs/reports/goal3128_v2_8_torch_partner_front_door_and_numba_boundary_2ai_consensus_2026-06-03.md`
- `docs/reports/goal3131_v2_8_torch_grouped_arg_front_door_local_smoke_2ai_consensus_2026-06-03.md`

## Review Questions

1. Does the v2.8 chain preserve the app-agnostic engine boundary?
2. Does the front door require explicit user partner selection and reject hidden
   dispatch / auto partner selection?
3. Are actual partner outputs now schema-consistent with the reference consumer
   for the covered operations?
4. Is local functional coverage correctly bounded, including the Numba local
   CUDA-stack boundary?
5. Are the claim boundaries clear: no release, no speedup, no broad RT-core, no
   true-zero-copy, no app-specific engine, no user-defined shader injection?
6. What must be done next before v2.8 can make stronger claims?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. Lead with findings by severity, then claim boundary, files inspected,
answers to the questions, and recommended next steps.
