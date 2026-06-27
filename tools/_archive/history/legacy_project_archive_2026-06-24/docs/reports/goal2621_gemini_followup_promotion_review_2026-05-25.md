To: RTDL Architecture Committee
Date: 2026-05-25
Subject: RTDL Goal2621 Formal Review: Contact-Manifold Benchmark and COLLECT_K_BOUNDED Stability

### Verdict
**PROMOTE.** The contact-manifold benchmark app and the `COLLECT_K_BOUNDED` primitive have satisfied all architectural gates, including backend parity and safety contracts.

### Boundary Assessment
*   **Engine Separation:** Verified. Native backends (Embree/OptiX) export only generic `COLLECT_K_BOUNDED` i64 row-collection symbols (`rtdl_embree_collect_k_bounded_i64`, `rtdl_optix_collect_k_bounded_i64`). 
*   **Domain Semantics:** All collision detection, contact-manifold interpretation, and mid-point metadata derivation remain strictly within the Python application layer or the standalone C++ CPU baseline. No collision-specific native engine logic has been introduced.
*   **ABI Integrity:** The witness-row schema `(query_group_id, query_triangle_id, scene_triangle_id)` is handled as a generic $k \times 3$ integer buffer, preserving the primitive's app-independent utility.

### Evidence Assessment
*   **Backend Parity:** Local Mac Embree parity and Linux RTX A5000 OptiX parity are confirmed. Native collection results match the deterministic Python oracle exactly for both `tiny` and `grid-512` fixtures.
*   **Safety Contract:** The **fail-closed overflow** policy is rigorously enforced. Both Python and native backends raise a `RuntimeError` and return zero partial rows when the candidate count exceeds `witness_capacity`.
*   **Baselines:** A standalone C++ CPU baseline (`cpp_contact_witness_baseline.cpp`) exists and provides a non-RTDL reference for collision overhead, fulfilling the required performance-comparison gate.

### Required Fixes
*   **None.** The previously identified ambiguity regarding the `overflow` dataset naming has been resolved by explicit documentation in the README and app source, clarifying that overflow is a capacity constraint rather than a scene property.

### Final Recommendation
1.  **Promote** `examples/v2_0/research_benchmarks/contact_manifold/` from a candidate to a **Promoted Benchmark App**. 
2.  **Promote** `COLLECT_K_BOUNDED` from experimental to a **Stable Primitive** in the `docs/rtdl_primitive_catalog.md`.
3.  **Update** `docs/application_catalog.md` to reflect the closure of the blocking gates (OptiX A5000 parity and C++ baseline).

*Note: This promotion authorizes the use of "Promoted Benchmark" wording in internal documentation but does not authorize public speedup claims or external release wording at this time.*

---
**Reviewer:** Gemini CLI Autonomous Agent
**Status:** Goal2621 Evidence Audit Complete
