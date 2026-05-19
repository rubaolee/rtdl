# Independent Gemini Review for Goal2384: Prepared 3D Neighbor Ranked Summary

**Reviewer**: Gemini / Google
**Date**: 2026-05-19
**Independent From**: Claude

## Verdict: `accept-with-boundary`

## Review Findings

1. **Does Goal2384 remain app-agnostic by exposing a prepared fixed-radius ranked-summary continuation, not an RTNN-specific native ABI?**
   - **Yes.** The new native ABI functions (`rtdl_optix_run_prepared_ranked_fixed_radius_neighbor_summaries_3d`, `fixed_radius_neighbors_3d_grid_ranked_summary`, etc.) and the Python API (`PreparedOptixFixedRadiusNeighbors3D.run_ranked_summary`) use generic, geometric terminology. There are no RTNN-specific structs, identifiers, or application logic hardcoded into the OptiX engine.

2. **Does the native `RtdlFixedRadiusRankedNeighborSummary` layout match the Python ctypes structure and the static assertions?**
   - **Yes.** The native layout defined in `src/native/optix/rtdl_optix_prelude.h` strictly contains `uint32_t query_id`, `uint32_t neighbor_count`, `uint32_t nearest_neighbor_id`, `uint32_t kth_neighbor_id`, `double nearest_distance`, `double kth_distance`, and `double sum_distance` (total size 40 bytes). Extensive `static_assert` statements verify these exact offsets. The Python `ctypes.Structure` in `src/rtdsl/optix_runtime.py` (`_RtdlFixedRadiusRankedNeighborSummary`) defines an identical sequence and typing of fields, guaranteeing ABI parity.

3. **Does the ranked-summary kernel preserve nearest/kth/sum semantics for the bounded `k_max <= 64` top-K set?**
   - **Yes.** The report details that the local top-K buffer is bounded to `k_max <= 64` (consistent with Goal2381), and the kernel keeps the nearest candidates in distance/id order. The small correctness oracle (`ranked_summary_correctness_small.json`) explicitly asserts and validates that the `nearest id`, `kth id`, `nearest distance`, `kth distance`, and `sum distance` are preserved accurately compared to the exact Python oracle.

4. **Do the pod artifacts support the report?**
   - **Yes.** 
     - **Small correctness oracle `ok: true`:** The report correctly states the small oracle reports `ok: true`.
     - **No host exact-refine:** The phase timings matrix shows `0.0` seconds spent in host exact-refine, demonstrating that computations have successfully stayed device-resident.
     - **One summary row per query:** The tables indicate that for 65,536 input queries, 65,536 output rows are emitted; and for 262,144 queries, 262,144 output rows are emitted, confirming a 1:1 query-to-summary relationship.
     - **Large case improves over both Goal2381 ranked witness rows and Goal2371 old host-refined rows:** For 262,144 points, the timing dropped from `0.090302s` (Goal2371) and `0.047824s` (Goal2381) down to just `0.008271s` (Goal2384). This shows significant improvement achieved by stripping away row materialization.

5. **Are the claim boundaries correct?**
   - **Yes.** The "Boundaries" section correctly restricts the claim. It explicitly rejects any authorization for:
     - RTNN paper-equivalence claims
     - RT-core nearest-neighbor claims
     - Arbitrary ANN claims
     - Broad nearest-neighbor acceleration claims
     - User-defined shader-extension claims

## Conclusion

Goal2384 successfully introduces a high-performance, device-resident ranked-summary continuation that avoids the heavy I/O cost of materializing full witness rows. The implementation honors the 100% app-agnostic mandate and is appropriately scoped. I approve this update under the `accept-with-boundary` verdict, validating the baseline for v2.2 performance scaling without overclaiming functionality.
