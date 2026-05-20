# Goal2456 Gemini Review: Goal2455 Grouped Stream Continuation Design

Date: 2026-05-19

## Review of: Goal2455 Generic Grouped Stream Continuation Design

This review covers the design document `docs/reports/goal2455_generic_grouped_stream_continuation_design_2026-05-19.md` and related context reports: `docs/research/future_version_to_do_list.md`, `tests/goal2455_generic_grouped_stream_continuation_design_test.py`, `docs/reports/goal2450_rt_dbscan_workspace_reuse_negative_evidence_2026-05-19.md`, and `docs/reports/goal2452_rt_dbscan_full_adjacency_planner_budget_2026-05-19.md`.

### Review Questions & Answers:

1.  **Does the design correctly identify the next RT-DBSCAN performance frontier after workspace reuse was measured as negative and planner budget was improved?**

    Yes. The `Goal2450_rt_dbscan_workspace_reuse_negative_evidence` report explicitly concludes that workspace reuse was not a performance win and identifies "lower-overhead generic grouped stream continuation" as the next real RT-DBSCAN improvement. This aligns directly with the core problem statement in Goal2455 regarding the limitations of full adjacency (memory-hungry) and chunking (launch-heavy). The `Goal2452_rt_dbscan_full_adjacency_planner_budget` report details an app-level policy improvement, but Goal2455 correctly targets a deeper primitive-level optimization.

2.  **Is the proposed primitive generic enough, or does it risk becoming a DBSCAN-specific native continuation?**

    The design strongly emphasizes generality, explicitly stating "No DBSCAN-native symbol" and requiring the use of "generic fixed-radius traversal, not a DBSCAN native ABI." The conceptual contract's operation descriptors (e.g., `grouped_count`, `grouped_union_candidate`) are also generic. The `future_version_to_do_list.md` reinforces the need to avoid DBSCAN-specific native ABIs. However, the design acknowledges the risk by listing "must prove it is not DBSCAN-specific" as a con for Option A. The first concrete target, `generic_fixed_radius_grouped_component_continuation_3d`, is directly applicable to DBSCAN, making the proof phase crucial for demonstrating its broader applicability. The intent is generic, but careful implementation and validation are needed to uphold this.

3.  **Are the non-goals and claim boundaries strict enough?**

    Yes, the non-goals and claim boundaries are appropriately strict. They clearly delimit the scope of this design, explicitly disavowing DBSCAN-native symbols, hidden dispatchers, paper-reproduction claims, release claims without further evidence, and user-defined shader injection. The design's claim boundary states it is "a design target only" and "does not authorize performance claims or release claims," which is suitable given the `needs-more-evidence` verdict.

4.  **Is Option A, native-driven generic union continuation, a reasonable first implementation path if reviewed carefully?**

    Yes, Option A (Native-Driven Generic Union Continuation) appears to be a reasonable first implementation path. It offers performance advantages like fewer CuPy launches and the removal of the neighbor-index table for the continuation path. The design acknowledges the primary risks: ensuring the primitive remains generic and handling atomic-min/union correctness. The `Recommended Path` section outlines a rigorous proof-of-concept process that includes a native design review, minimal OptiX implementation, validation against multiple references, and targeted pod-smoke testing. This structured approach to address the identified risks makes Option A a justifiable first step.

5.  **What must be proven before implementation can move from `needs-more-evidence` to accepted?**

    The design document explicitly lists the following proofs required:
    *   A design review handoff for the exact native ABI names and metadata.
    *   Implementation of a minimal OptiX path for fixed-radius grouped union candidate continuation.
    *   Verification that app-facing RT-DBSCAN code continues to call a generic RTDL primitive.
    *   Validation of exact label signatures against a CPU reference, full adjacency, and chunked adjacency.
    *   Pod-smoke testing at both a 32,768-point scale (to confirm no regression against full adjacency) and a larger scale where full adjacency is over budget (to demonstrate the intended performance gain over chunking).

### Verdict:

`needs-more-evidence`

The design correctly identifies a critical performance bottleneck and proposes a generic primitive solution. The non-goals and claim boundaries are strict, and the proposed implementation path (Option A) is reasonable, provided the outlined proof steps are rigorously followed. The current verdict of `needs-more-evidence` is appropriate as the design itself acknowledges the need for further validation of its generality, correctness, and performance benefits before full acceptance for implementation.
