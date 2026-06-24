## M24 External Review — Barnes-Hut Severe-Regression Blocker

**Verdict: `accept_with_boundary`**

---

### Findings

**1. Root-cause diagnosis: confirmed, credible**

The before-fix micro-probe is decisive. Non-prepacked OptiX scalar query median ~0.033s vs prepacked ~0.00017s is a ~194x ratio that is fully explained by Python point-packing being fused into the measured query call. The before-fix focused repro (V3 OptiX 32768 = 0.071077s vs V2.14 = 0.041552s) is consistent with this: the regression was measurement contamination, not algorithmic slowdown. The 131072 near-tie (0.295900 vs 0.296358) further supports this — at larger node counts the traversal dominates, washing out the packing artifact.

**2. Implementation quality: generic, not benchmark-tuning**

The fix introduces a typed API — `prepare_query_points`, `PackedPoints` — that changes the contract for both Embree and OptiX paths together. This is a proper API-level fix, not a benchmark-specific shortcut. The metadata flag `query_points_prepacked_by_caller` is explicit and inspectable. 64 passing tests across three suites is adequate coverage for the scope stated.

**3. Repeat-50 evidence: real, but context-conditional**

The repeat-50 speedups (17.8x at 32768, 22.8x at 131072) are genuine for the stated pattern. However, the prepare costs are material and must be surfaced:

- 32768: prepare = 0.113272s, 50 queries = 0.008010s → single-query effective cost ≈ **0.113s vs V2.14's ~0.043s (~2.6x slower for single use)**
- 131072: prepare = 0.489708s, 50 queries = 0.038259s → single-query effective cost ≈ **0.490s vs V2.14's ~0.241s (~2.0x slower for single use)**

Break-even is approximately **N ≥ 4 repeated queries per prepared payload**. Below that threshold, V3 post-fix is slower than V2.14. This is not a blocker for the fix itself, but it is a hard boundary on any claim.

**4. Primary blocker: conditionally closed, not definitively closed**

The M22 whole-app Barnes-Hut geomean was **0.831x**. The focused 4-row after-fix geomean is 15.811x, and the repeat-50 pattern is compelling. But **no post-fix whole-app geomean rerun was submitted**. Without it, we cannot verify the app-level metric now sits above the 0.900x severe-regression floor. The whole-app benchmark may contain single-query node-coverage patterns; if so, the prepare-cost penalty applies and the geomean could still be below floor. This gap prevents unconditional closure.

**5. Boundaries: correct direction, one gap**

Codex's stated boundaries — prepared/repeated-query only, internal RTDL, not single-run wall-time, not external zero-copy, not embedding — are correctly scoped. The single-query regression vs V2.14 at both tested sizes is not explicitly called out and must be added to the boundary statement.

---

### Required Before M24 Can Fully Close

| # | Item | Hard gate? |
|---|------|-----------|
| 1 | Whole-app Barnes-Hut geomean rerun on same RTX 4000 Ada POD, confirming ≥ 0.900x | **Yes — release blocker** |
| 2 | Explicit documented boundary: single-query use incurs prepare penalty; V3 is slower than V2.14 for N < ~4 queries per prepared payload | **Yes — required for honest boundary** |
| 3 | Confirm that no broad V3-over-V2 geomean or whole-app Barnes-Hut claim appears in any release-facing text | **Yes — scope fence** |
| 4 | 2-AI consensus counter-signature after item 1 evidence is produced | **Yes — process gate** |

---

### Explicit Non-Authorization

This review does **not** authorize release, does not authorize broad V3-over-V2 performance wording, does not authorize whole-app Barnes-Hut claims, and does not authorize embedding, external zero-copy, or all-app rerun claims. The fix is technically sound and the root-cause diagnosis is accepted. Conditional closure of the Barnes-Hut severe-regression blocker is granted only upon submission of a passing whole-app geomean rerun (≥ 0.900x) with the single-query penalty boundary explicitly stated.
