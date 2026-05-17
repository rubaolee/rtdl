# Independent Gemini Review: Goal2280 Direct-Index Negative A/B Probe

**Review Document:** `docs/reviews/goal2281_gemini_review_goal2280_direct_index_negative_probe_2026-05-17.md`

## Context

This independent review, conducted by Gemini/Antigravity, assesses the findings of Goal2280 concerning the rejection and reversion of direct-index host exact refinement in RTDL v2.0. The previous Goal2279 attempted to optimize segment-pair intersection performance by threading direct primitive indices, but A/B evidence did not support its retention. Goal2280 serves as negative evidence, confirming this decision.

## Review Questions and Answers

### 1. Does the same-pod A/B evidence justify rejecting/reverting direct-index host exact refinement?

**Yes.** The A/B evidence presented in `docs/reports/goal2280_direct_index_refinement_negative_ab_probe_2026-05-17.md`, supported by the JSON reports (`goal2280_direct_index_ab_baseline_goal2276_pod_2026-05-17.json` and `goal2280_direct_index_ab_current_goal2279_pod_2026-05-17.json`), clearly justifies the rejection and reversion. The candidate implementation (Goal2279) showed a performance regression for "raw witness rows" (speedup of 0.944x) and was effectively neutral for "exact scalar count" (speedup of 1.004x) compared to the Goal2275 cached-lookup baseline. This lack of improvement or observed degradation provides sufficient evidence for its rejection. It is important to note that per-artifact `improvement_vs_goal2276` fields are legacy probe helper fields and are not the canonical same-pod A/B authority for Goal2280.

### 2. Are the claim boundaries correct and narrow?

**Yes.** The claim boundaries articulated in `docs/reports/goal2280_direct_index_refinement_negative_ab_probe_2026-05-17.md` are appropriately narrow and correct. The allowed claim explicitly limits its scope to the specific hardware (RTX A5000), workload (RayJoin-exported 100k LSI stream), and the tested feature (direct-index host exact refinement versus Goal2275 baseline). The "Not allowed" claims explicitly prevent over-generalization (e.g., broad speedup claims, RayJoin paper reproduction, RTDL beating RayJoin), ensuring that the findings are interpreted strictly within the measured context.

### 3. Does the report correctly point future work toward generic device-resident or partner-continuation paths, without adding RayJoin-specific engine logic?

**Yes.** The report consistently points future work in the correct direction. The "Decision" section of the probe report and the "Device-Resident Prepared Scene Output Streams" section in `docs/research/future_version_to_do_list.md` advocate for prioritizing generic device-resident or partner-continuation paths. This strategic guidance aims to avoid candidate copyback and host exact refinement, focusing on broader optimizations rather than RayJoin-specific engine logic or further host metadata micro-optimizations, which aligns with the goal of improving generic prepared segment-pair intersection performance.

### 4. Does the current source appear restored to the accepted cached-lookup shape, with no direct candidate-index ABI remaining in the segment-pair record?

**Yes.** Verification through `tests/goal2280_direct_index_refinement_negative_ab_probe_test.py` and direct inspection of `src/native/optix/rtdl_optix_core.cpp` confirms that the source code has been restored. The `SegmentPairIntersectionRecord` struct within `kSegmentPairIntersectionKernelSrc` no longer contains `left_index` or `right_index`, indicating that the direct candidate-index ABI has been successfully removed, restoring the code to its Goal2275 cached-lookup shape.

## Verdict

**accept**

This independent review by Gemini/Antigravity confirms the findings of Goal2280, independently validating the decision to reject and revert the direct-index host exact refinement based on the provided A/B evidence and the strategic direction for future RTDL development.
