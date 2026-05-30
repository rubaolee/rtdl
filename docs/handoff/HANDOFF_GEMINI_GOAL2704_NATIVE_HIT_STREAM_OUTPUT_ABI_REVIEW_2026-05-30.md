# Gemini Review Task: Goal2704 Native Hit-Stream Output ABI Contract

Please perform an independent read-only review of Goal2704.

## Files To Inspect

- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/optix_runtime.py`
- `tests/goal2704_native_hit_stream_output_abi_contract_test.py`
- `docs/reports/goal2704_native_hit_stream_output_abi_contract_2026-05-30.md`

## Review Questions

1. Does Goal2704 define a generic native CUDA hit-stream column ABI without app
   or benchmark-specific vocabulary?
2. Does `prepare_native_device_hit_stream_columns_from_abi(...)` correctly keep
   native raw CUDA pointers in an experimental, claim-bounded state?
3. Does the metadata preserve the boundaries that true zero-copy, public
   speedup, and native promotion remain unauthorized until pod evidence proves
   same-pointer/no-host-stage behavior and native cleanup?
4. Does `optix_runtime.py` merely name the future symbol without pretending the
   native implementation exists?
5. Are there any risks before Goal2705 starts native C++/OptiX work?

## Required Output

Write your review to:

`docs/reviews/goal2705_gemini_review_goal2704_native_hit_stream_output_abi_2026-05-30.md`

Use one of these verdicts only: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.
