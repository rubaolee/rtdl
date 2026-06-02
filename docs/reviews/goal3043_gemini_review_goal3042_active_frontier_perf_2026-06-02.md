# Gemini Review: Goal3042 Active-Frontier Hausdorff Performance

**Date:** 2026-06-02

**Verdict:** accept-with-boundary

## Review Questions and Answers

### 1. Does the native OptiX change remain generic and app-agnostic?

Yes, the native OptiX change remains generic and app-agnostic. The new native function `rtdl_optix_nearest_max_distance_active_frontier_row` in `src/native/optix/rtdl_optix_api.cpp` and `src/native/optix/rtdl_optix_workloads.cpp` operates on generic `query_point` and `geometry_group` arguments and radius parameters. It does not contain any Hausdorff-specific logic or naming conventions, and its output (a single row with `query_id`, `neighbor_id`, and `distance`) is also generic. This is explicitly confirmed by checks in the provided test and report, such as `app_specific_native_engine_logic_authorized: false`.

### 2. Do the Python app and lab preserve exact Hausdorff semantics and original input witness indices?

Yes, the Python application (`rtdl_hausdorff_v2_function.py`) and language lab (`rtdl_hausdorff_v2_language_lab.py`) correctly preserve exact Hausdorff semantics and original input witness indices. The artifact `goal3042_active_frontier_perf_a4000_2026-06-02.json` reports `"all_rows_match_exact_reference": true` and `"runtime_smoke_matched_openmp_witness": true`. The Python code, particularly in the `_reduce_nearest_max_distance_row` and `_reduce_nearest_witness_rows` functions, correctly reconstructs original source and target indices from IDs returned by the native code, and the overall logic correctly computes the undirected Hausdorff distance.

### 3. Are the A4000 timing ratios in the summary artifact correct?

Yes, the A4000 timing ratios in the summary artifact (`goal3042_active_frontier_perf_a4000_2026-06-02.json`) are correct. Manual calculation of the `best_active_speedup_vs_cupy` from the raw `elapsed_sec` values for `cupy_grouped_grid_rawkernel` and `rtdl_rt_grouped_active_frontier_nearest_witness` (for the 131072x131072 point set) yields approximately 6.536, which matches the reported `best_active_speedup_vs_cupy` value precisely. The included test also programmatically verifies these ratios.

### 4. Is the claim language properly bounded as internal v2.6 evidence rather than public release/speedup/true-zero-copy authorization?

Yes, the claim language is properly bounded. All relevant documents and the generated artifact explicitly state that this is "Internal v2.6 performance evidence" and requires external review before any public claims. The artifact contains boolean flags (e.g., `"v2_6_release_authorized": false`, `"public_speedup_claim_authorized": false`, `"true_zero_copy_claim_authorized": false`, `"rt_core_speedup_claim_authorized": false` for broad claims) that consistently limit the scope of this evidence. The `V2_6_ROADMAP_CLAIM_BOUNDARY` in `src/rtdsl/v2_6_roadmap.py` further reinforces these boundaries, preventing unauthorized public claims.

### 5. What should Codex do next before a public Hausdorff RT-core performance claim?

Before a public Hausdorff RT-core performance claim, Codex should:

1.  **Integrate Review Feedback:** Address any feedback arising from this Gemini review and the parallel Claude review.
2.  **Expand Hardware and Dataset Validation:** Conduct more extensive testing across a broader range of RT-core enabled GPUs (beyond just A4000) and with more diverse real-world and synthetic datasets to ensure the robustness and generalizability of the performance gains.
3.  **Refine Claim Language:** Collaborate closely with product and marketing teams to develop precise, highly bounded, and verifiable public claim language. This language must strictly adhere to the `V2_6_ROADMAP_CLAIM_BOUNDARY` to avoid broad, whole-app, or general RT-core speedup claims without further comprehensive evidence.
4.  **Update Public Documentation:** Ensure all public-facing documentation accurately reflects the new capabilities, specific performance characteristics, and any limitations or contextual requirements for the claims.
5.  **Address Broader Roadmap Items:** Review and clarify other roadmap items flagged as `not_speedup_evidence` or `true_zero_copy_still_blocked` if they are directly relevant to the proposed public RT-core performance claim to avoid inconsistencies or misinterpretations.

---
**Summary:** Goal3042 successfully introduces a generic, app-agnostic native OptiX active frontier witness selection mechanism. The Python app and lab correctly implement Hausdorff semantics and preserve witness indices. The reported A4000 performance ratios are accurate and represent a significant speedup for the specific benchmark. The claim language is appropriately bounded, preventing premature public assertions.
