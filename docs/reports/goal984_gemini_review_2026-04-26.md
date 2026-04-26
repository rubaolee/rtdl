# Goal984 Graph OptiX Single-Launch Gate Review

**Date:** 2026-04-26

**Reviewer:** Gemini

**Decision:** ACCEPT

**Reasoning:**

The proposed changes in Goal984, which move the graph OptiX cloud gate from chunked visibility execution to a single visibility launch by default using `--chunk-copies 0`, are **ACCEPTED**. This is a conservative and logical pre-cloud optimization aimed at reducing launch/setup overhead and allowing for a cleaner measurement of OptiX graph visibility path performance.

Here are the concrete reasons supporting this decision:

1.  **Conservative Pre-Cloud Optimization:** The documentation `docs/reports/goal984_graph_optix_single_launch_gate_2026-04-26.md` clearly states that this is a "pre-cloud optimization" designed to "measure a lower-overhead OptiX graph visibility path." The motivation section explains that the previous chunking likely inflated overhead. `scripts/goal889_graph_visibility_optix_gate.py` correctly implements `chunk_copies=0` to perform a single visibility launch, aligning with this goal.

2.  **Chunked Diagnostics Remain Available:** The design explicitly ensures that chunked diagnostics are still available. `docs/reports/goal984_graph_optix_single_launch_gate_2026-04-26.md` notes, "Positive `--chunk-copies N` still runs chunked diagnostics." This is supported by the logic in `scripts/goal889_graph_visibility_optix_gate.py`, which retains chunking functionality for positive `chunk_copies` values, and indirectly verified by `tests/goal889_graph_visibility_optix_gate_test.py`.

3.  **Consistency Across Files (with minor correction):**
    *   The intent and implementation of `--chunk-copies 0` are largely consistent across the main documentation, `scripts/goal889_graph_visibility_optix_gate.py`, and `scripts/goal759_rtx_cloud_benchmark_manifest.py`.
    *   An inconsistency was identified in `scripts/goal914_rtx_targeted_graph_jaccard_rerun.py`, where a `ValueError` prevented `--graph-chunk-copies 0` from being used, despite the `docs/rtx_cloud_single_session_runbook.md` explicitly instructing its use. This has been remediated by modifying the validation in `scripts/goal914_rtx_targeted_graph_jaccard_rerun.py` to allow non-negative values for `graph_chunk_copies` and updating the corresponding error message.
    *   All specified tests in `docs/reports/goal984_graph_optix_single_launch_gate_2026-04-26.md` pass, further confirming the correct behavior.

4.  **Public RTX Speedup Claims Remain Unauthorized:** All reviewed documents consistently and explicitly state that public RTX speedup claims related to these changes (and generally for graph analytics) are **UNAUTHORIZED**.
    *   `docs/reports/goal984_graph_optix_single_launch_gate_2026-04-26.md` states, "It does not authorize public RTX speedup claims."
    *   `docs/rtx_cloud_single_session_runbook.md` reiterates this in its "Claim Boundary" section.
    *   `docs/reports/goal978_rtx_speedup_claim_candidate_audit_2026-04-26.json` explicitly shows `"public_speedup_claim_authorized_count": 0` and for the `graph_analytics` entry, recommends `"reject_current_public_speedup_claim"` because RTX is currently slower than the fastest non-OptiX same-semantics baseline.

The change facilitates a more accurate performance measurement and maintains the strict control over public speedup claims, which is crucial for data integrity. The identified and resolved inconsistency further strengthens the robustness of the implementation.
