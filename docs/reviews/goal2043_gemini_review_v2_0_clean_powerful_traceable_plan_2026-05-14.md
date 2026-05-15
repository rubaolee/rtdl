# Goal2043 Gemini Review: v2.0 Clean, Powerful, Traceable Plan

**Date:** 2026-05-14

**Reviewer:** Gemini

**Document Reviewed:** `docs/reports/goal2043_v2_0_clean_powerful_traceable_plan_2026-05-14.md`

## Overview

This plan comprehensively addresses the identified design gaps for the v2.0 release, focusing on establishing clean, powerful, consistent, and traceable continuation contracts at the partner layer. It correctly prioritizes generic solutions over app-specific engine customizations and lays out a detailed execution strategy.

## Review Questions Addressed

1.  **Does Goal2043 correctly identify the real design gap as generic partner continuation/reduction contracts rather than app-specific engine customization?**
    *   **Yes.** The plan explicitly and correctly identifies that the native RTDL engines should remain app-agnostic, emitting only generic geometric or relational rows. It clearly delegates the responsibility for continuation policies (filtering, grouping, ranking, segmented reductions, witness preservation, topology assembly, and user-defined kernels) to the partner layer. This distinction is crucial for maintaining a clean and extensible architecture, and the document consistently reinforces this principle throughout. The analysis of remaining unsolved rich requirements (e.g., exact K=3 facility fallback ranking, exact ANN ranking, exact Hausdorff with witness extraction, broad general polygon overlay) further solidifies the need for generic partner contracts.

2.  **Are the proposed contracts clean and app-agnostic: candidate rows, segmented reductions, group top-K, threshold decisions, witness extraction, polygon topology split, and user-defined partner kernels?**
    *   **Yes.** Each proposed contract is designed with app-agnosticism as a core principle.
        *   **Candidate Row Contract:** Defines a backend-neutral schema with stable identity fields, abstracting away memory venue differences.
        *   **Segmented Reduction Contract:** Positions reductions as a reusable partner operator family, preventing app-specific duplication.
        *   **Top-K Ranking Contract:** Introduces a generic `topk_by_group` primitive, explicitly avoiding app-specific naming.
        *   **Threshold Decision Contract:** Elevates existing threshold logic to a documented partner primitive, ensuring consistent semantics.
        *   **Witness Extraction Contract:** Casts witness extraction as a generic `argmax_of_group_min` style contract.
        *   **Polygon Topology Contract:** Wisely splits the problem into candidate pair discovery, exact pair contribution summary, and optional topology assembly, clarifying boundaries and documenting `bbox_broadphase` as a partner policy.
        *   **User-Defined Partner Kernel Contract:** Clearly defines RawKernel as a partner capability, not an engine customization, with strict boundaries for labeling and claims.
    The overall approach ensures that these contracts are generic, reusable, and maintain a clear separation of concerns.

3.  **Does the plan preserve a consistent Embree/OptiX story while respecting that Embree uses host-memory partners and OptiX uses device-memory partners?**
    *   **Yes.** The plan effectively preserves a consistent conceptual contract for both Embree and OptiX. It clearly states that "Embree and OptiX expose the same conceptual contract," and that "the public contract is the same even though the physical memory venue differs." The plan acknowledges the underlying memory differences (host for Embree/NumPy/Torch-CPU and device for OptiX/CuPy/Torch-CUDA) but ensures semantic consistency at the partner operator level.

4.  **Are the traceability and performance evidence rules strong enough for v2.0 release preparation?**
    *   **Yes.** The traceability and performance evidence rules outlined are robust and comprehensive. The definition of "Traceable" requires every public claim to map to a test, artifact, report, and review, with clear explanations of speedup sources and unsolved boundaries. The "Release Audit" phase includes multi-AI reviews (Codex, Claude, Gemini) and mandates artifact manifests linking claims to evidence. The "Performance Evidence Rules" are highly detailed, requiring specific metadata (backend, partner, scale, hardware, commit hash, command, median time, correctness status, claim boundary) for every performance row, along with specific requirements for OptiX (pod evidence, subpath timing for RT-core claims) and Embree. These rules are indeed strong enough for a rigorous v2.0 release preparation.

5.  **Is the recommended Goal2044 next step reasonable, or should another primitive come first?**
    *   **Yes, the recommended Goal2044 next step is highly reasonable.** Beginning with "Phase A: Contract Documentation" and the first "Phase B: NumPy Reference Layer" primitives (segmented reductions, group top-K, witness-carrying reductions), followed by converting a complex app path like exact Hausdorff with witness extraction, is a sound strategy. This approach establishes the foundational documentation and CPU-based reference implementations, which are critical for validating the generic contract design before moving to GPU implementations. It directly addresses the "real design gap" without resorting to ad-hoc, app-specific fixes that would undermine the "clean, consistent, or explainable" goals of v2.0.

## Conclusion

The Goal2043 plan is exceptionally well-structured and demonstrates a clear understanding of the architectural and engineering challenges for v2.0. It provides a robust framework for developing generic, high-performance, and well-documented partner continuation contracts, which is essential for the long-term maintainability and extensibility of RTDL. The emphasis on explicit contracts, consistent behavior across backends, and rigorous traceability is commendable.

**Verdict:** `accept`
