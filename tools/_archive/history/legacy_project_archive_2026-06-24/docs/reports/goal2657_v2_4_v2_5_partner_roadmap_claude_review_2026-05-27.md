---

# Critical Review: Goal2657 v2.4/v2.5 Partner Roadmap

**Reviewer:** Claude (Sonnet 4.6)
**Date:** 2026-05-27
**Reviewed files:** `goal2657_v2_4_v2_5_partner_roadmap_2026-05-27.md`, `benchmark_app_performance.md`, `benchmark_app_performance_3ai_consensus.md`, `partner_acceleration_boundaries.md`, `application_catalog.md`

---

## 1. Verdict

**Accept with fixes.**

The architecture is sound. v2.4 as protocol cleanup before any partner addition, v2.5 as Triton-first partner, and the explicit "no app-specific semantics in the native engine" rule are all correct positions. The performance gates are well-placed and the no-public-claim discipline is maintained. However, there are non-trivial weaknesses in the Triton-first justification, the 10% tolerance band calibration, and the v2.5 exit gate that should be resolved before 3-AI consensus.

---

## 2. Blocking Issues

None.

---

## 3. Non-Blocking Issues

### 3a. Triton-first rationale is circumstantial, not evidenced

The "Why Triton First" section argues Triton is "designed for GPU tensor kernels" and "can express reductions, compaction, tiling, and row-finalization work." Both statements are true, but they are the wrong framing: RT continuation work (CSR-offset row streaming, compact/filter columns, bounded-collect finalization) is not tensor work in the ML tiling sense. Triton's core strength is tiled GEMM-shaped operations. The continuation primitives listed — segmented count/sum, compact/filter/mask, bounded collect — look more like custom CUDA scatter/gather patterns, which Numba `@cuda.jit` also handles.

The roadmap does not cite any measurement or prior work showing Triton outperforms Numba for these exact continuation shapes. "Less predictable deployment profile" for Numba is asserted without data. Triton also has its own deployment complexity: specific LLVM/CUDA versions, incomplete support for non-ML tiling patterns, and known limitations on pre-Ampere hardware.

**Recommendation:** Either cite at least one external reference or a small internal experiment showing Triton handles segmented reduction or compact/filter better than Numba for GPU RT post-processing workloads, or soften the wording to "preferred first target pending implementation findings, with Numba promoted if Triton proves unsuitable for the continuation primitives."

### 3b. The 10% tolerance band is not calibrated to the weakest rows

Gate 2 says a promoted path must stay "within roughly 10 percent" of the current best path. The benchmark portfolio spans 3.29x (Hausdorff) to 172.14x (RTNN). For a weak row like Hausdorff, a 10% regression on a 3.29x speedup yields ~2.96x — which is barely above 3x and is the row where the performance case is already weakest. For RTNN at 172x, a 10% regression to ~155x changes nothing materially.

The uniform 10% band implicitly protects strong rows more than weak ones. The roadmap should either acknowledge this asymmetry explicitly or specify that the Hausdorff and Robot Collision rows (the two rows below 6x) have a tighter tolerance (e.g., must remain ≥ 3x and ≥ 5x respectively, rather than relative percent).

**Recommendation:** Add a note that for rows where the current speedup is less than 6x, the absolute floor matters more than the relative percent, and name the specific floors.

### 3c. "Within 10%" does not specify which phase the tolerance applies to

Gate 2 references the current-best-path comparison. Gate 6 requires phase timing splits. But the two are not connected: if a Triton adapter adds 15% overhead to the continuation phase but reduces it 50% overall relative to the prior partner path, does that pass Gate 2? The 10% tolerance should explicitly state it applies to the same-phase comparison used in the original benchmark row — for example, "traversal + continuation combined" for rows where continuation is part of the primary measurement, or "traversal-only" for rows measured traversal-only.

**Recommendation:** Add one sentence to Gate 2 specifying that the tolerance applies to the same phase contract recorded in the accepted benchmark row.

### 3d. v2.5 exit gate requires only 3 of 10 apps — that's weak

The v2.4 exit gate requires all 10 promoted apps to retain their basis. The v2.5 exit gate requires at least 3 promoted apps with a promoted Triton path. This asymmetry means v2.5 could be declared done with 7 of 10 apps having no new partner path at all. There is no requirement that the remaining apps have even a labeled compatibility or learner Triton path.

**Recommendation:** Add language that the remaining 7 apps must be at minimum classified as one of: (a) Triton not yet attempted, (b) Triton learner/preview path exists but not promoted, or (c) Triton reviewed and explicitly deferred. This prevents silent omission from looking like completion.

### 3e. No fallback criterion for when Triton should yield to Numba per-app

The roadmap positions Numba as "secondary or exploratory after the protocol is stable." But it never defines when an app-specific finding during v2.5 implementation should flip the ordering. If Triton proves unsuitable for row-streaming continuation on triangle counting, what happens? The roadmap implies Triton is always the answer and Numba is only general exploration, but the actual work may reveal per-app suitability differences.

**Recommendation:** Add one sentence: "If Triton proves unsuitable for a specific continuation pattern during v2.5 implementation, that pattern may be piloted with Numba under the same performance gate; the overall Triton-first ordering does not preclude Numba from being the better technical fit for individual primitives."

### 3f. CuPy demotion wording needs care

The roadmap says "RawKernel strings are too close to asking users to write CUDA kernels by hand." This is technically accurate but potentially misleading as a principle. CuPy RawKernels in the current source tree are the mechanism that makes several benchmark apps work. Labeling CuPy as merely a "compatibility and conformance partner" without acknowledging that the v2.4 protocol work will produce generic continuation contracts that must be validated against existing CuPy paths risks implying CuPy paths will be demoted before replacements exist.

**Recommendation:** Add language to the CuPy item clarifying that CuPy paths remain as the reference conformance baseline during v2.4 protocol work, and that a CuPy partner path is not deprecated until a Triton or Numba path passes the same performance gate for the same benchmark row.

### 3g. Hardware qualifier missing from performance gate table

The roadmap's performance basis table lists raw speedup numbers (3.29x, 38.36x, etc.) without the hardware qualifier. The v2.3 benchmark consensus already required the RTX A5000 qualifier. A reader of the roadmap in isolation sees the numbers without knowing they are RTX A5000 measurements.

**Recommendation:** Add a footnote or table note: "All current basis rows measured on NVIDIA RTX A5000 pod evidence." Consistent with what the 3-AI consensus required for the v2.3 appendix.

### 3h. Two source documents cited but not included in the review packet

The roadmap cites `goal2654_all_benchmark_app_perf_comparison_refresh_2026-05-27.md` and `goal2655_benchmark_rt_core_speedup_summary_2026-05-27.md` as part of the current performance basis, but neither was included in this review packet. The numbers in the roadmap table are consistent with `benchmark_app_performance.md` and `application_catalog.md`, so there is no apparent discrepancy. However, for a 3-AI consensus packet, all cited source documents should be present.

**Recommendation:** Include both documents in the review packet, or add a note confirming they are available and that the roadmap table numbers were reconciled against them.

---

## 4. Benchmark Performance Basis: Correct

The roadmap correctly identifies the 10 promoted benchmark apps and their 11 primary rows. The speedup values in the roadmap table match the values in `benchmark_app_performance.md` and `application_catalog.md` exactly. The roadmap correctly notes that RayDB has two distinct rows (27.67x count, 104.00x sum) rather than conflating them. The "exact-subpath internal evidence, not public whole-app claims" framing is preserved and matches the 3-AI consensus position. No overclaiming is present in the table. This section passes.

---

## 5. Triton-First / Numba-Secondary Ordering: Partially Justified

The ordering is defensible but not strongly evidenced. The strongest argument is negative: Numba's deployment profile and JIT overhead for high-throughput segmented GPU work are legitimate concerns, and CuPy RawKernels are correctly identified as too low-level for the user-effort goal. The weaker argument is positive: the claim that Triton is better for these continuation shapes than Numba is asserted, not demonstrated. Triton's actual strength is tiled GPU operations for ML, which is not what RT continuation requires. The ordering is acceptable as a starting position but should be framed as a hypothesis to be confirmed in early v2.5 implementation rather than as a settled architectural fact. See Issue 3a for the required fix.

---

## 6. App-Specific Semantics Risk: Well-Controlled in Gates, Moderate Risk in Practice

Gate 7 ("no app-specific semantics may enter the native engine") is correctly stated and is reinforced in the v2.5 candidate pilot table — each pilot row explicitly names what must not happen (no DBSCAN-native ABI, no contact/collision native ABI, no replacement of the RT-core triangle-count path with a graph kernel). The initial Triton partner scope is appropriately generic (compact/filter/mask, segmented count/sum/min/max, bounded collect, grouped argmin, row-stream chunk finalization).

The residual risk is social rather than structural: all five v2.5 pilot apps are from the benchmark set. A developer working on a RayDB Triton adapter under performance pressure will feel the pull of "just one RayDB-specific reduction shortcut." The roadmap currently relies on Gate 7 as the enforcement mechanism, but there is no specified audit artifact (e.g., a "native-engine vocabulary audit" result) required before a pilot app is declared complete.

**Recommendation:** The v2.4 audit-native-engine-vocabulary deliverable (Goal 6) is the right mechanism. Make it explicit that this audit output is a required input to the v2.5 pilot gate, not just a v2.4 cleanup task.

---

## 7. Required Changes Before 3-AI Consensus

These are the minimum changes needed. None are blocking to the architectural direction; all are precision and completeness issues.

| # | Change | Severity |
|---|--------|----------|
| R1 | Add hardware qualifier (RTX A5000) to the performance basis table or as a table footnote | Low; the 3-AI consensus already required this for the v2.3 appendix |
| R2 | Gate 2: specify that the 10% tolerance applies to the same phase contract used in the accepted benchmark row | Medium; without this, tolerance comparisons are ambiguous |
| R3 | Gate 2: acknowledge the asymmetric risk for weak rows (<6x) and name explicit absolute floors for Hausdorff and Robot Collision | Medium; a 10% regression on 3.29x is materially worse than on 172x |
| R4 | "Why Triton First": soften absolute language or add at least one reference/experiment supporting Triton over Numba for segmented reduction/compact continuation | Medium; the current framing is a strong claim with no evidence |
| R5 | v2.5 exit gate: require that non-piloted apps be explicitly classified (not yet attempted / learner path exists / deferred) rather than silently absent | Low-medium |
| R6 | Add one sentence establishing a per-app fallback path from Triton to Numba if Triton proves unsuitable for a specific continuation pattern | Low |
| R7 | CuPy demotion: clarify CuPy paths remain as conformance reference until a replacement passes the same performance gate | Low |
| R8 | Include goal2654 and goal2655 in the review packet, or add a reconciliation note | Low; completeness only |

---

## Summary

The roadmap is architecturally correct and well-disciplined. The "protocol first, partner second" sequencing is the right call. The no-app-specific-semantics rule is explicit and enforced at multiple levels. The main weaknesses are precision issues: the Triton-first rationale is asserted rather than evidenced, the 10% tolerance band is not calibrated to the weakest rows, and the v2.5 exit gate is under-specified relative to the v2.4 gate. Applying R1–R8 above would produce a document ready for 3-AI consensus.
