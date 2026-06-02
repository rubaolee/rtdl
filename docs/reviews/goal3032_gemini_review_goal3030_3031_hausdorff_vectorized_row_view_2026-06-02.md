# Independent Gemini Review: Goal3030/Goal3031 Hausdorff Vectorized Row-View

**Date:** 2026-06-02

## Review Summary

This independent review assesses the changes introduced by Goal3030 and Goal3031, focusing on the Hausdorff vectorized raw row-view implementation within the RTDL OptiX backend. The work aims to improve the performance of exact Hausdorff distance calculations by leveraging a vectorized NumPy view for host-side reduction of raw row data, while strictly adhering to established honesty and claim boundaries.

## Findings

1.  **`OptixRowView.to_numpy()` contract:**
    *   **Finding:** The `OptixRowView.to_numpy()` method in `src/rtdsl/optix_runtime.py` correctly presents a borrowed host-memory view. It explicitly includes a docstring and internal claim flags that state it is "not a device-memory or zero-copy partner handoff claim," and this is validated by `tests/goal3030_optix_row_view_numpy_reducer_test.py`.
    *   **Assessment:** **Acceptable.** The contract is clear and validated.

2.  **Hausdorff raw-row method implementation:**
    *   **Finding:** The Hausdorff raw-row method, specifically `_directed_rt_grouped_adaptive_raw_nearest_witness` in `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`, remains exact and operates entirely at the app-layer. It uses generic OptiX primitives, and the reduction from the raw row-view is performed using NumPy operations on the host. There is no evidence of Hausdorff-specific native ABI or engine customization, as confirmed by the lack of such symbols in `src/rtdsl/optix_runtime.py` and explicit statements in `docs/reports/goal3031_hausdorff_vectorized_row_view_l4_pod_2026-06-02.md` and `examples/v2_0/research_benchmarks/hausdorff_xhd/README.md`.
    *   **Assessment:** **Acceptable.** The implementation respects the generic nature of the native engine.

3.  **L4 pod evidence representation:**
    *   **Finding:** The `docs/reports/goal3031_hausdorff_vectorized_row_view_l4_pod_2026-06-02.md` report and its accompanying JSON artifact accurately represent the L4 pod evidence. The vectorized raw row-view path demonstrates a measurable performance improvement (22-27% faster) over the older adaptive RT row path. However, it explicitly and clearly states that it is "still slower than the dense CuPy grouped-grid reference." This is quantitatively supported by the `raw_vs_old_ratio` (less than 1.0) and `raw_vs_cupy_ratio` (greater than 1.0) in the artifact and validated by `tests/goal3031_hausdorff_vectorized_row_view_l4_pod_test.py`.
    *   **Assessment:** **Acceptable.** The evidence is honestly presented and validated.

4.  **Claim boundaries:**
    *   **Finding:** All specified claim boundaries are rigorously maintained. The report `docs/reports/goal3031_hausdorff_vectorized_row_view_l4_pod_2026-06-02.md` explicitly lists that it "does not authorize: v2.6 release, public speedup wording, broad RT-core speedup wording, whole-app speedup wording, true zero-copy wording, package-install claims, app-specific native-engine behavior." This aligns with the `V2_6_ROADMAP_CLAIM_BOUNDARY` in `src/rtdsl/v2_6_roadmap.py` and is verified by the claim flags in the JSON artifact and corresponding unit tests (`tests/goal3031_hausdorff_vectorized_row_view_l4_pod_test.py`).
    *   **Assessment:** **Acceptable.** Boundaries are intact and consistently applied.

5.  **Test adequacy and residual risks:**
    *   **Finding:** The unit tests (`tests/goal3030_optix_row_view_numpy_reducer_test.py` and `tests/goal3031_hausdorff_vectorized_row_view_l4_pod_test.py`) adequately cover the technical implementation of the `OptixRowView` to NumPy conversion, the app-layer vectorized reduction, and the adherence to honesty and performance claim boundaries.
    *   **Residual Risks:**
        *   **Performance Gap:** The primary residual risk is the remaining performance gap between the optimized RTDL/OptiX path and the CuPy grouped-grid reference. The report correctly identifies that further improvements will likely require a generic device-resident active-set and sparse candidate-frontier continuation contract to avoid repeated host-side data transfer and reduction.
        *   **Generalizability:** Performance was measured on L4 pods. While an improvement, the behavior on diverse hardware or datasets remains a consideration for broader claims.
    *   **Assessment:** **Adequate.** Tests are sufficient for the internal nature of this performance-tuning goal, with clear identification of future work and inherent limitations.

## Verdict

`accept-with-boundary`

This work successfully implements a performance improvement for the internal Hausdorff benchmark, validates its correctness, and rigorously adheres to all specified honesty and claim boundaries. The identified residual performance gap with the CuPy reference is acknowledged, along with a clear direction for future optimization work.

This review is for internal v2.6 performance-tuning evidence only. It does not authorize release or public claims.
