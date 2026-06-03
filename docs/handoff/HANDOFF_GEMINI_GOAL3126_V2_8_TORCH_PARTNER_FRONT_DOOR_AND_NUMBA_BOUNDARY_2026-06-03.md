# Handoff: Gemini Review For Goal3126 v2.8 Torch Partner Front Door And Numba Boundary

Please review Goal3126 and write the review to:

`docs/reviews/goal3127_gemini_review_goal3126_torch_partner_front_door_and_numba_boundary_2026-06-03.md`

## Scope

Goal3126 continues v2.8 partner-consumer front-door hardening:

- filters `bounded_collect_finalize_i64` partner output to canonical columns
  `group_ids`, `item_ids`, and `row_offsets`;
- adds a dependency-free unit test to enforce that `counts` does not leak
  through the v2.8 bridge;
- records local Linux Torch CUDA smoke for `grouped_topk_f64` and
  `bounded_collect_finalize_i64`;
- records that local Linux Numba validation is blocked because even a trivial
  Numba CUDA kernel destroys the context on the GTX 1070 host.

## Files To Inspect

- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py`
- `src/rtdsl/partner_continuation_protocol.py`
- `docs/reports/goal3126_v2_8_torch_partner_front_door_and_numba_local_boundary_2026-06-03.md`
- `docs/reports/goal3125_v2_8_partner_consumer_named_output_hardening_2ai_consensus_2026-06-03.md`

## Review Questions

1. Is filtering bounded-collect output to `group_ids`, `item_ids`, and
   `row_offsets` correct relative to the canonical partner-continuation
   protocol?
2. Does the Torch smoke substantiate local functional parity for
   `grouped_topk_f64` and `bounded_collect_finalize_i64`?
3. Is the Numba CUDA context failure correctly classified as a local host/Numba
   stack boundary rather than an RTDL grouped-arg verdict?
4. Are the claim boundaries correct?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. Include findings by severity, claim boundary, files inspected, and
next step.
