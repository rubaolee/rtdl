# Goal3127: Gemini Review For Goal3126 v2.8 Torch Partner Front Door And Numba Boundary

**Verdict:** accept-with-boundary

**Findings By Severity:**
*   **Low:** Numba CUDA context failure. While Numba's `cuda.is_available` reports true, Numba kernels (even trivial ones) fail at `cuda.synchronize` with `CUDA_ERROR_CONTEXT_IS_DESTROYED`. This is explicitly classified as a local host/Numba stack boundary and not an RTDL grouped-arg verdict, indicating it's external to the current RTDL work.

**Claim Boundary:**
The current work operates within strict boundaries: local functional smoke only; no release, no public speedup, no broad RT-core, no true-zero-copy, no hidden dispatch, no automatic partner selection, no app-specific native-engine behavior, no user-defined shader injection, and no benchmark-app performance claims.

**Evidence Considered:**
*   Goal3126 focuses on hardening the v2.8 explicit partner-consumer front-door.
*   The canonical protocol for `bounded_collect_finalize_i64` specifies `output_names=("group_ids", "item_ids", "row_offsets")`.
*   Code changes correctly filter lower-level `bounded_collect_finalize_i64` partner output to these canonical columns, preventing auxiliary counts from leaking through the v2.8 bridge.
*   A dependency-free unit test confirms that `v2.8` outputs correctly exclude `counts` when `bounded_collect_finalize_i64_partner_columns` returns `group_ids`, `item_ids`, `row_offsets`, and `counts`.
*   Windows validation passed with `py_compile` and 27 focused tests.
*   Local Linux Torch smoke tests on 192.168.1.20 / GTX 1070 / Torch 2.5.1+cu121 passed for `grouped_topk_f64` and `bounded_collect_finalize_i64` against the Goal3114 Python reference consumer.
    *   Torch `topk` output: groups `[0,0,1,1,2]`, items `[12,10,20,21,30]`, scores `[0.5,1.5,0.25,0.75,9.0]`, claim flags `false`.
    *   Torch `bounded collect` output keys `['group_ids','item_ids','row_offsets']`; groups `[0,0,1,2,2]`, items `[10,11,20,30,31]`, offsets `[0,2,3,5]`, claim flags `false`.
*   Local Linux Numba target exhibits `CUDA_ERROR_CONTEXT_IS_DESTROYED` with even trivial Numba kernels, despite `cuda.is_available` being true. This Numba CUDA context failure is classified as a local host/Numba stack boundary, not an RTDL grouped-arg verdict.

**Review Question Answers:**
1.  **Is filtering bounded-collect output to group_ids, item_ids, and row_offsets correct relative to the canonical partner-continuation protocol?**
    *   Yes, the filtering is correct. The code change explicitly aligns with the canonical protocol by only exposing `group_ids`, `item_ids`, and `row_offsets`, preventing extraneous data like auxiliary counts from leaking through the v2.8 bridge.
2.  **Does the Torch smoke substantiate local functional parity for grouped_topk_f64 and bounded_collect_finalize_i64?**
    *   Yes, the local Linux Torch smoke tests successfully substantiated functional parity for `grouped_topk_f64` and `bounded_collect_finalize_i64`, showing expected output for both functions.
3.  **Is the Numba CUDA context failure correctly classified as a local host/Numba stack boundary rather than an RTDL grouped-arg verdict?**
    *   Yes, the Numba CUDA context failure is correctly classified as a local host/Numba stack boundary, indicating an issue with the local environment or Numba stack rather than a defect in the RTDL grouped-arg implementation itself.
4.  **Are the claim boundaries correct?**
    *   Yes, the claim boundaries are correct and appropriately limit the scope of the current validation, acknowledging that the work is confined to local functional smoke tests without broader performance or deployment claims.

**Next Step:**
Use a pod or comparable CUDA host with a healthy selected partner stack to validate `grouped_argmin_f64` and `grouped_argmax_f64` through the explicit v2.8 front door.
