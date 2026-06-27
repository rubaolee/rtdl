# Gemini Review: Goals4070-4071 RT-DBSCAN Route Positioning

Date: 2026-06-09
Verdict: `accept`

## Summary

This review covers Goals 4070 and 4071, which evaluated the `device_count_then_emit` memory-pressure option at the app level and refreshed RT-DBSCAN route-positioning evidence following the partition-preview chain.

## Evidence Evaluation

### Goal 4070: Memory-Pressure Option

Goal 4070 correctly identifies that `device_count_then_emit` provides significant memory-pressure relief (13.13x to 209.35x reduction in partition pair capacity) but incurs a performance penalty (typically 5-11% slower) due to the extra device-side counting pass. The conclusion that this should remain an explicit user-selected option rather than the default is well-supported by the pod timing data.

### Goal 4071: Route Positioning Refresh

Goal 4071 correctly compares the normalized component-size signatures across different app-level schemas (`cluster_sizes` vs `component_sizes`). The evidence demonstrates that while the partition-convergence route is a functional graph-component candidate, it remains significantly slower (7.2x) than the recommended RT-core grouped-stream Numba route on the measured 65,536-point clustered profile.

## Claim Boundary Audit

All claim boundaries are strictly closed:
- No release authorization.
- No public speedup wording.
- No broad RT-core speedup wording.
- No whole-app benchmark claims.
- No paper-reproduction claims.
- No hidden dispatch or automatic partner selection.
- No app-specific native engine logic or native ABI additions.
- No true-zero-copy claims.

The evidence is correctly framed as internal route-positioning and memory-pressure analysis.

## Responses to Handoff Questions

1. **Does Goal 4070 correctly conclude that `device_count_then_emit` is an explicit memory-pressure option?**
   Yes. The 13x-209x capacity reduction is significant, and the 5-11% overhead justifies keeping it as an optional mode rather than the default.

2. **Does Goal 4071 correctly compare normalized component-size signatures?**
   Yes. The `_component_size_signature` helper in the script correctly extracts and sorts sizes from both `component_sizes` and `cluster_sizes` formats, ensuring a valid correctness comparison.

3. **Does the evidence support keeping the RT-core grouped-stream Numba route as the recommendation?**
   Yes. With a 6.1x-12.8x performance advantage over same-component-size opponents, the RT-core path remains the superior benchmark default.

4. **Are all claim boundaries closed?**
   Yes. Both reports and pod artifacts explicitly verify that all relevant claim flags are false and the boundary text is present.

5. **What should be the next engineering target?**
   To achieve real performance gains rather than more timing evidence, focus should shift toward optimizing the RT-core stream compaction or reducing the Numba-to-Python boundary overhead in the signature path, rather than further partition-preview iterations which have reached diminishing returns.

## Final Verdict

The deliverables are technically sound, the conclusions are data-driven, and the claim boundaries are properly enforced.

**Verdict: `accept`**
