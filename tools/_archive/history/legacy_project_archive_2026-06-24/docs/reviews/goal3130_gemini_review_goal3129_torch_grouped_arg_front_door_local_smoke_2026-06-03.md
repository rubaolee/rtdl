# Goal3130: Gemini Review For Goal3129 v2.8 Torch Grouped-Arg Front Door Local Smoke

**Verdict:** accept-with-boundary

## Findings By Severity

**High:** Local Linux Torch functional smoke tests successfully validated `grouped_argmin_f64` and `grouped_argmax_f64` against Python references, confirming functional parity for these operations within the defined boundaries.

**Moderate:** The combined coverage with Goals3123 and 3126 ensures local functional smoke covers all operations currently listed in `V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_SUPPORTED_OPERATIONS` through at least one healthy explicit partner.

**Low (Known Limitation):** Numba-specific validation remains open due to context destruction issues on the local Numba CUDA stack, even for trivial independent kernels. This is an acknowledged boundary of this review and not a blocker for the current goal's scope.

## Claim Boundary

This review is strictly bounded by:
*   Local functional smoke only.
*   No release claims.
*   No public speedup claims.
*   No broad RT-core claims.
*   No true-zero-copy claims.
*   No hidden dispatch claims.
*   No automatic partner selection.
*   No app-specific native-engine behavior.
*   No user-defined shader injection.
*   No benchmark-app performance claims.

## Evidence Considered

*   Goal3129 records local Linux Torch functional smoke for v2.8 explicit partner-consumer front-door `grouped_argmin_f64` and `grouped_argmax_f64`.
*   Execution environment details: Host 192.168.1.20, checkout `/home/lestat/work/rtdl_codex_local_check`, commit `c8d58e78`, GTX 1070, Torch 2.5.1+cu121 from isolated target.
*   Specific output matches for `grouped_argmin_f64` and `grouped_argmax_f64` against Python references.
*   Combined coverage statement with Goals3123 and 3126 for `V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_SUPPORTED_OPERATIONS`.
*   Statement regarding Numba-specific validation remaining open due to CUDA context issues.
*   Explicit list of claim boundaries.
*   Next pod-class work items.

## Review Question Answers

1.  **Does the Torch smoke substantiate local functional parity for grouped_argmin_f64 and grouped_argmax_f64?** Yes, the `grouped_argmin_f64` and `grouped_argmax_f64` outputs matched the Python reference, substantiating local functional parity within the stated boundaries.
2.  **Is the coverage table accurate and bounded?** Yes, the coverage statement for `V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_SUPPORTED_OPERATIONS` is accurate and clearly bounded to local functional smoke through at least one healthy explicit partner.
3.  **Is it correct to keep Numba-specific validation open despite Torch grouped argmin/argmax passing?** Yes, it is correct to keep Numba-specific validation open. The evidence indicates a distinct issue with the local Numba CUDA stack (context destruction) that is separate from the successful Torch validations and needs independent resolution.
4.  **Are the claim boundaries correct?** Yes, the provided claim boundaries are clear, comprehensive, and appropriate for a local functional smoke test.

## Next Step

The next pod-class work should focus on:
*   Numba-specific grouped arg validation on a healthy CUDA stack.
*   Timing/performance separation.
*   Larger stream sizes.
*   Claim-boundary enforcement.
