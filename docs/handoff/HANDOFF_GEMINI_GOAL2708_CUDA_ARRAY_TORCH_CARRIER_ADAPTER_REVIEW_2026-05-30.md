# Handoff: Goal2708 CUDA-Array Hit-Stream to Torch Carrier Adapter Review

Please perform an independent read-only review of Goal2708.

## Files To Inspect

- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/__init__.py`
- `tests/goal2708_hit_stream_cuda_array_torch_carrier_adapter_test.py`
- `docs/reports/goal2708_hit_stream_cuda_array_torch_carrier_adapter_2026-05-30.md`
- Relevant prior context:
  - `docs/reports/goal2704_native_hit_stream_output_abi_contract_2026-05-30.md`
  - `docs/reports/goal2706_native_optix_hit_stream_device_columns_2026-05-30.md`
  - `docs/reviews/goal2707_gemini_review_goal2706_native_optix_hit_stream_device_columns_2026-05-30.md`

## Questions

1. Does Goal2708 correctly close the immediate adapter gap between raw
   CUDA-array-interface native hit-stream columns and the Triton/Torch carrier
   gather path?
2. Does the code fail closed for host columns unless `allow_explicit_copy=True`
   and for missing torch/CuPy/DLPack runtime support?
3. Does the report avoid overclaiming true zero-copy, same-pointer behavior,
   hardware proof, or public performance speedup before RTX pod validation?
4. Are the tests sufficient for the no-pod contract slice, with pod execution
   correctly left as the next evidence step?

## Required Output

Write the review to:

`docs/reviews/goal2709_gemini_review_goal2708_cuda_array_torch_carrier_adapter_2026-05-30.md`

Use one of the accepted verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.
