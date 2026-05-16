# Independent Gemini Review of Goal2157 RayJoin Public-CDB Nonzero LSI Evidence

Date: 2026-05-16

This is an independent Gemini review, distinct from Codex. It does not authorize v2.0 release by itself.

## Review Questions and Answers

1.  **Does Goal2157 correctly distinguish bounded derived public-CDB slice evidence from full RayJoin paper reproduction?**
    *   **Answer:** Yes. The report `docs/reports/goal2157_rayjoin_public_cdb_nonzero_lsi_slice_evidence_2026-05-16.md` explicitly states under "Method" that "The slices are bounded derived inputs, not exact RayJoin paper-scale inputs." Furthermore, the "Claim Boundary" section clearly disclaims "full RayJoin paper reproduction" and "paper-scale performance claims." The corresponding POD JSON files (`goal2157_rayjoin_public_cdb_nonzero_lsi_slice_pod_2026-05-16.json` and `goal2157_rayjoin_public_cdb_nonzero_lsi_larger_slices_pod_2026-05-16.json`) also contain `"full_rayjoin_reproduction": false` within their `claim_boundary` sections, reinforcing this distinction.

2.  **Do the artifacts support the reported nonzero LSI row counts and parity claims?**
    *   **Answer:** Yes. The report details nonzero LSI row counts for `count48` (34 intersections), `count128` (56 intersections), and `count192` (85 intersections). These counts are consistently reflected across all backends (CPU, Embree, OptiX) within the `row_counts` arrays in both `goal2157_rayjoin_public_cdb_nonzero_lsi_slice_pod_2026-05-16.json` and `goal2157_rayjoin_public_cdb_nonzero_lsi_larger_slices_pod_2026-05-16.json`. Additionally, all backends consistently report `"all_parity_vs_cpu_python_reference": true` in the POD JSONs, which is summarized as "all pass" in the report's results table. The test file `tests/goal2157_rayjoin_public_cdb_nonzero_lsi_slice_evidence_test.py` programmatically verifies these nonzero row counts and parity claims.

3.  **Is the narrow OptiX performance statement for the `count192` slice justified by the artifact?**
    *   **Answer:** Yes. The report states in its "Interpretation" that "warm OptiX is substantially faster than both CPU and Embree" for the `count192` slice, and its "Claim Boundary" authorizes "a narrow statement that warm OptiX is faster than CPU and Embree on the measured `count192` bounded slice." The "Results" table in the report shows median `app_elapsed_sec` for `count192` as CPU: 0.016114s, Embree: 0.029917s, OptiX: 0.003110s. The `goal2157_rayjoin_public_cdb_nonzero_lsi_larger_slices_pod_2026-05-16.json` artifact confirms these median values, showing OptiX achieving approximately 5.18x speedup over CPU and 9.62x over Embree. This data strongly justifies the narrow performance statement.

4.  **Does the report avoid broad RT-core, whole-app RayJoin, paper-scale, and v2.0 release claims?**
    *   **Answer:** Yes. The "Claim Boundary" section of the report explicitly lists several disclaimers: "full RayJoin paper reproduction," "paper-scale performance claims," "broad RT-core speedup claims," "whole-app RayJoin acceleration claims," and "v2.0 release authorization." The POD JSON files mirror these disclaimers with corresponding `false` values for `broad_rt_core_speedup_claim_authorized`, `full_rayjoin_reproduction`, `paper_scale_perf_claim_authorized`, and `v2_0_release_authorized`. This demonstrates a clear and consistent effort to avoid making broad, unauthorized claims.

5.  **What caveats should be tracked before using this as a public v2.0 benchmark row?**
    *   **Answer:** The report itself outlines several important caveats and next steps under its "Next Work" section:
        *   **Reproducibility/Reusability:** The current offset search and slice timing are "one-off" and need to be turned into a "committed reusable runner."
        *   **Comprehensive Comparison:** The addition of "CUDA/CuPy non-RT baselines for the same nonzero LSI slices" is needed for a more complete performance picture.
        *   **Scalability/Broader Applicability:** Further work is required to "search for larger nonzero county/soil and other public RayJoin family slices that run in seconds." The current slices are "bounded derived inputs, not exact RayJoin paper-scale inputs."
        *   **Public Benchmark Decision:** The decision "whether RayJoin LSI should become a first-class v2.0 public benchmark row" is pending further development and review, explicitly including this independent review.
    *   The report's overall verdict is "It is not release evidence by itself," indicating that while a strong development result, it needs further maturation for public benchmark status.

## Verdict

`accept-with-boundary`

Goal2157 successfully identifies and measures bounded public-CDB RayJoin LSI slices with nonzero intersections, providing valuable development evidence. The report, supported by the artifacts, is meticulous in defining its scope and claim boundaries, particularly regarding the distinction from full paper reproduction, paper-scale claims, and v2.0 release authorization. The OptiX performance gain on the `count192` slice is clearly justified. The identified caveats, such as the need for reusable runners, additional baselines, and larger slices, are appropriately listed as "Next Work" items within the report itself. This result is a strong step forward in RayJoin LSI development, but further work, as acknowledged, is required before it can be considered a first-class v2.0 public benchmark row.