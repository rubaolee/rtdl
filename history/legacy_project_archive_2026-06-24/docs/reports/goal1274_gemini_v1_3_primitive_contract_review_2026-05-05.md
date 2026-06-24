I will start by reading the three specified reports to understand the context of the roadmap, validated findings, and the current draft contract.

The RTDL v1.3 Primitive ABI and Per-App Lowering Contract draft has been reviewed against the Goal1255 roadmap and Goal1273 v1.2 validated findings. The draft is architecturally sound and strictly compliant with previous consensus.

### Review Verdict: `ACCEPT`

### Analysis and Rationale

1.  **Primitive Set Consistency:** The draft correctly preserves the v1.5 target set established in Goal1255 and Goal1042. The decision to explicitly split `REDUCE` by operation (`MIN`, `MAX`, `SUM`) and data type (`FLOAT`, `INT`) is an excellent architectural improvement. This avoids the "opaque reduction" anti-pattern and ensures that tolerance and overflow policies are declared upfront.
2.  **Backend Scope Enforcement:** The contract explicitly restates and enforces the pre-v2.1 freeze on Vulkan, HIPRT, and Apple RT. By focusing the ABI requirement on Embree and OptiX, it ensures engineering resources remain concentrated on the primary performance and comparison lanes.
3.  **Evidence-Grounded Lowering:** The per-app lowering matrix accurately reflects the v1.2 pod findings. Specifically:
    *   **Graph/DB Analytics:** Correctively identifies `ANY_HIT` and `REDUCE_INT(COUNT)` as the core primitive targets while explicitly excluding broad SQL or graph-database claims.
    *   **Polygons:** Strategically retains app-specific continuations for area calculations until generic float reduction contracts are stabilized, preventing premature generalization.
    *   **Jaccard:** Honestly preserves the `optix_still_slower_with_reason` status, using it as a diagnostic row rather than attempting to over-promote it.
4.  **Operational Maturity (Gates & ABI):** The inclusion of a mandatory `prepared` execution mode (reusable scene/probe state) directly addresses the v1.2 observation that preparation and packing can dominate query time. The "Phase Gate" requiring separate timing for traversal vs. copyback vs. reduction is critical for identifying future bottlenecks.

### Non-Blocking Suggestions

*   **Precision Policy:** For `REDUCE_FLOAT(SUM)`, consider explicitly mentioning Kahan summation or similar compensation techniques as optional "precision_policy" flags if future v1.5 validation shows high error on very large scales.
*   **Experimental `COLLECT_K`:** While correctly marked as experimental, ensure that the "result_layout" for `COLLECT_K_BOUNDED` includes a requirement to define the behavior when the hit count exceeds `k` (e.g., truncation vs. error).

### Conclusion
The draft successfully transitions from empirical performance evidence (v1.2) to a formal architectural contract (v1.3). It provides the necessary "Contract Gate" and "Migration Gate" infrastructure required to safely begin v1.4 implementation work.

**Verdict: ACCEPT**
