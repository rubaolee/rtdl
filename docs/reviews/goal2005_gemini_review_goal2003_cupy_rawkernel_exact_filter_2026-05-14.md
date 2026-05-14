# Goal2005 Gemini Review of Goal2003 CuPy RawKernel Exact Witness Filter

Status: accept-with-boundary

Date: 2026-05-14

## Review of Goal2003 Work

This review covers the Goal2003 work on implementing a CuPy RawKernel for exact witness filtering, focusing on the provided files and addressing the specific questions posed.

**Files Reviewed:**
- `src/rtdsl/partner_adapters.py`
- `docs/reports/goal2003_cupy_rawkernel_exact_witness_filter_2026-05-14.md`
- `tests/goal2003_cupy_rawkernel_exact_witness_filter_test.py`
- `docs/reports/goal2003_pod_smoke/segment_polygon_cupy_rawkernel_hitcount_perf.json`
- Relevant Goal2000 context from `docs/reports/goal2000_optix_candidate_witness_exact_filter_pod_audit_2026-05-14.md` and related review documents.

---

### Questions and Answers:

1.  **Does Goal2003 preserve the app-agnostic native-engine boundary by keeping OptiX output generic candidate witnesses?**
    *   **Answer:** Yes. The `docs/reports/goal2003_cupy_rawkernel_exact_witness_filter_2026-05-14.md` explicitly states in its "Scope" section that "The native OptiX engine remains app-agnostic: it still emits only generic ray/primitive candidate witness pairs." This is further reinforced by the contract metadata `native_engine_row_contract: generic_ray_primitive_candidate_witness_pairs` and the implementation in `partner_adapters.py` where native OptiX calls are used to produce these generic witnesses before partner-specific filtering.

2.  **Is the CuPy RawKernel exact segment/triangle filter correctly scoped as a partner/app-layer exact filter rather than native engine customization?**
    *   **Answer:** Yes. The "Scope" section of the Goal2003 report clarifies that the "Goal2003 moves the segment/polygon hit-count exact-filter step from host Python to the CuPy partner layer." The report consistently refers to this as an "app-side RawKernel exact segment/triangle filter." The "Design Lesson" section further solidifies this by stating "RTDL native should produce generic candidate tables, while partner adapters provide reusable GPU-side exact filters and reductions." The implementation in `partner_adapters.py` and the accompanying tests confirm this architectural separation.

3.  **Is it honest to set `whole_app_true_zero_copy_authorized: true` only for the CuPy hit-count column path while leaving row/Torch paths bounded?**
    *   **Answer:** Yes, it is honest. The report clearly distinguishes the CuPy hit-count column path, where the entire process (filtering and reduction) happens on the device without host materialization, warranting `whole_app_true_zero_copy_authorized: true`. Conversely, the report explicitly states that "For Torch and fake test runtimes, the existing host exact filter remains in place. That path still records `whole_app_true_zero_copy_authorized: false`." This precise and conditional authorization for zero-copy based on the processing pipeline is appropriate and transparent.

4.  **Do the pod artifacts support the limited performance claim for the hit-count column path at counts 2048 and 8192?**
    *   **Answer:** Yes. The `docs/reports/goal2003_pod_smoke/segment_polygon_cupy_rawkernel_hitcount_perf.json` artifact provides concrete evidence. For both 2048 and 8192 counts, the `v2_cupy` results show `status: "pass"` and `all_one: true` (indicating correctness). Furthermore, the `ratio_vs_v1_8_median` values (0.098x for 2048 and 0.013x for 8192) demonstrate significant performance improvements, supporting the limited speedup claim. The report also correctly calls out the RawKernel compile latency for the first iteration.

5.  **What risks remain before v2.0 release?**
    *   **Answer:** As outlined in the "Boundary" section under "Still blocked" in the Goal2003 report, the following risks remain:
        *   V2.0 release authorization.
        *   Broad RT-core speedup wording.
        *   Whole-app claims for Python row materialization paths.
        *   Torch parity for device-side exact filtering.
        *   Final all-app v2.0 versus v1.8 performance matrix.

---

## Verdict

**accept-with-boundary**

The Goal2003 work successfully delivers on its stated objectives, demonstrating a clear understanding of the native engine boundary and correctly scoping the CuPy RawKernel exact filter as a partner-layer optimization. The documentation is thorough, and the provided pod artifacts support the performance claims for the specific hit-count column path. The explicit enumeration of remaining risks is appreciated and aligns with a strategic, phased release approach. The "Design Lesson" also provides valuable architectural guidance for future development.