# Review of Goal1845 Witness Contract

**Reviewer:** Gemini
**Date:** 2026-05-13

## Review Questions and Verdicts:

1.  **Is the new witness output contract the right next step after the boolean `any_hit_flags` output, rather than trying to reconstruct identity in an app-level adapter?**
    *   **Verdict:** `accept`
    *   **Reasoning:** The report explicitly states that Goal1845 is the "correct next step" to preserve hit identity at the partner-owned output boundary, avoiding the need for app-level reconstruction from boolean flags. The implementation of `rtdl_optix_write_prepared_ray_anyhit_2d_device_witnesses` with distinct ray and primitive IDs supports this.

2.  **Does the implementation preserve the correct boundary: one first-hit witness per ray, not the full multi-hit segment/polygon row collector?**
    *   **Verdict:** `accept`
    *   **Reasoning:** The contract is clearly defined as a "first-hit witness contract," preserving identity for the first primitive. The code (`rtdl_optix_workloads.cpp`) uses a `0xFFFFFFFFu` sentinel for no-hit and payload updates are consistent with capturing a single hit. Python tests also verify "first-hit witness" and "not all-hit collection," confirming this boundary is maintained.

3.  **Are the Python validators strict enough for same-device contiguous `uint32` output columns?**
    *   **Verdict:** `accept`
    *   **Reasoning:** The Python tests (`tests/goal1845_optix_partner_witness_output_contract_test.py`) include explicit checks for `uint32` data types and correct buffer shapes. Attempts to use `float32` or incorrect shapes raise `ValueError`, demonstrating strict validation of the required output column properties.

4.  **Are the public claim boundaries correct, especially no v2.0 release, no broad RT-core speedup, and no full app-level `segment_polygon_anyhit_rows` claim?**
    *   **Verdict:** `accept-with-boundary`
    *   **Reasoning:** The report clearly sets boundaries, stating that a v2.0 release requires more evidence and that the current contract is not a full replacement for `segment_polygon_anyhit_rows`. The Python tests confirm that `rt_core_speedup_claim_authorized` is false, aligning with the stated public claim boundaries.

5.  **What should the next engineering goal be: pod-validate this first-hit witness contract, or design the bounded all-witness output contract first?**
    *   **Verdict:** `needs-more-evidence`
    *   **Reasoning:** The report indicates that "No pod validation was run for Goal1845" and that "Hardware evidence must still be collected on an NVIDIA pod before this contract can be counted as execution evidence." This explicitly states that more evidence (through pod validation) is required before proceeding, making "needs-more-evidence" the appropriate verdict for the next engineering goal's status.
