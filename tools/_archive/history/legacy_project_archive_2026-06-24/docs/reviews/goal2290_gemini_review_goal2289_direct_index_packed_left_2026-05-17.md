# Goal2290: Gemini Review For Goal2289

**Verdict:** `accept-with-boundary`

## Review Questions

### 1. Does Goal2289 correctly distinguish the new packed-left scope from the rejected Goal2280 tuple-input scope?

Yes, Goal2289 clearly distinguishes its new packed-left scope from the rejected Goal2280 tuple-input scope. The `goal2289_packed_left_direct_index_segment_pair_2026-05-17.md` document explicitly states that Goal2280's rejection was due to Python tuple packing dominating the tuple-input path, which masked any benefits of direct indexing. Goal2289 re-evaluates direct indexing within the context of the packed-left contract established by Goal2287, where the native exact-refinement phase's performance impact is more visible. This distinction is crucial and well-articulated across the documentation.

### 2. Does the source change preserve the public segment-pair row contract while avoiding RayJoin-specific or app-specific native logic?

Yes, the source changes described in Goal2289 preserve the public segment-pair row contract and avoid RayJoin-specific or app-specific native logic. The `goal2289_packed_left_direct_index_segment_pair_2026-05-17.md` document explicitly states that the OptiX segment-pair any-hit candidate row continues to carry the public `left_id`/`right_id`. The addition of dense `left_index`/`right_index` values is for internal host exact refinement optimization, with the existing id-map lookup retained as a fallback. This ensures the public Python row contract remains unchanged. The claim of being "generic engine plumbing" without adding "RayJoin-specific native logic" is supported by the `tests/goal2289_packed_left_direct_index_segment_pair_test.py` which asserts the presence of the new indices in generic C++ structures and verifies the stated lack of RayJoin-specific logic in the report.

### 3. Do the two same-pod A/B artifact pairs support the narrow claim that direct candidate indices improve repeated prepared segment-pair calls under the packed-left contract?

Yes, the two same-pod A/B artifact pairs strongly support the narrow claim. The `goal2289_packed_left_direct_index_segment_pair_2026-05-17.md` report's summary table and the underlying JSON artifacts (`goal2289_direct_index_packed_ab_run1_baseline_2026-05-17.json`, `goal2289_direct_index_packed_ab_run1_candidate_2026-05-17.json`, etc.) consistently show performance improvements.

*   **Run 1:** Raw Speedup of 1.095x and Count Speedup of 1.038x.
*   **Run 2:** Raw Speedup of 1.252x and Count Speedup of 1.189x.

The phase telemetry data within the JSON artifacts further confirms that the `exact_refine` phase, which is directly impacted by this optimization, shows reduced median times in the candidate runs compared to the baselines. This provides clear evidence of improvement in the specific scenario tested.

### 4. Are the claim boundaries sufficiently strict?

Yes, the claim boundaries are sufficiently strict. The "Allowed claim" in `goal2289_packed_left_direct_index_segment_pair_2026-05-17.md` is highly specific, referencing the exact hardware (`RTX A5000 pod`), workload (`RayJoin-exported 100k LSI stream`), and programming contract (`prepacked-left contract`). It quantifies the improvement with a precise range (`1.1x` to `1.25x` for raw rows and `1.04x` to `1.19x` for scalar count). The "Not allowed" section explicitly prohibits overgeneralization, such as claims of whole application speedup, overturning Goal2280's rejection, or broad RT-core speedups, which is appropriate given the narrow scope of the optimization.
