# Gemini Review of Goal2907-2912 v2.5 Performance Packet

Date: 2026-05-31
Reviewer: Gemini

## Review Task

Independent read-only review of the recent v2.5 performance hardening chain from Goal2907 through Goal2912.

**Main question:** Did the current source tree honestly move from noisy short-row performance targets to a clean, scale-stable internal v2.5 packet, without adding app-specific native engine logic or overclaiming release/public speedup readiness?

## Verified Facts

1.  **Goal2912 packet is from commit `cf3a479d7f40c36df1b3f44f68de20ef1b098221`.**
    *   **VERIFIED.** Confirmed in `docs/reports/goal2912_current_packet_scaled_defaults_2026-05-31.md`, `docs/reports/goal2912_current_packet_scaled_defaults_pod/goal2855_summary.json`, and `tests/goal2912_current_packet_scaled_defaults_test.py`.
2.  **Goal2912 packet summary is `all_pass: true`, `artifact_count: 7`, `source_dirty: []`, and `claim_boundary_violations: {}`.**
    *   **VERIFIED.** Confirmed in `docs/reports/goal2912_current_packet_scaled_defaults_pod/goal2855_summary.json` and `tests/goal2912_current_packet_scaled_defaults_test.py`.
3.  **Goal2912 triage has `performance_targets: []` and `top_priority: null`.**
    *   **VERIFIED.** Confirmed in `docs/reports/goal2912_current_packet_scaled_defaults_triage_2026-05-31.json` and `tests/goal2912_current_packet_scaled_defaults_test.py`.
4.  **RTNN scaled defaults use `65,536` points and repeat `9`.**
    *   **VERIFIED.** Confirmed in `scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py` and `tests/goal2911_scale_stable_canonical_perf_rows_test.py`.
5.  **Hausdorff scaled defaults use `8,192 x 8,192` points and repeat `9`.**
    *   **VERIFIED.** Confirmed in `scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py` and `tests/goal2911_scale_stable_canonical_perf_rows_test.py`.
6.  **RTNN Goal2912 ratios are all green: uniform about `1.150x`, clustered about `2.522x`, shell about `7.640x` CuPy/RTDL.**
    *   **VERIFIED.** Confirmed in `docs/reports/goal2912_current_packet_scaled_defaults_triage_2026-05-31.json`, `docs/reports/goal2912_current_packet_scaled_defaults_2026-05-31.md`, and `tests/goal2912_current_packet_scaled_defaults_test.py`.
7.  **Hausdorff Goal2912 RTDL/CuPy ratio is about `0.940x`.**
    *   **VERIFIED.** Confirmed in `docs/reports/goal2912_current_packet_scaled_defaults_triage_2026-05-31.json`, `docs/reports/goal2912_current_packet_scaled_defaults_2026-05-31.md`, and `tests/goal2912_current_packet_scaled_defaults_test.py`.
8.  **RT-DBSCAN remains green at about `4.166x` to `4.857x` vs prepared CuPy grid.**
    *   **VERIFIED.** Confirmed in `docs/reports/goal2912_current_packet_scaled_defaults_triage_2026-05-31.json`, `docs/reports/goal2912_current_packet_scaled_defaults_2026-05-31.md`, and `tests/goal2912_current_packet_scaled_defaults_test.py`.
9.  **Barnes-Hut remains acceptable through measured partner selection: Torch selected, Triton visible but unpromoted, OptiX membership speedup about `154.306x`.**
    *   **VERIFIED.** Confirmed in `docs/reports/goal2912_current_packet_scaled_defaults_triage_2026-05-31.json`, `docs/reports/goal2912_current_packet_scaled_defaults_2026-05-31.md`, and `tests/goal2912_current_packet_scaled_defaults_test.py`.
10. **The chain does not claim release readiness, public speedup, whole-app speedup, broad RT-core speedup, true zero-copy, package install, automatic Triton selection, or paper reproduction.**
    *   **VERIFIED.** Consistently stated in the "Boundary" sections of all relevant reports and confirmed by the `claim_boundary` field in `docs/reports/goal2912_current_packet_scaled_defaults_triage_2026-05-31.json`, as well as `src/rtdsl/v2_5_internal_readiness.py` and `tests/goal2912_current_packet_scaled_defaults_test.py`.

## Review Questions

1.  **Is the move from short-row 4K/32K defaults to 8K/65K defaults technically justified as benchmark stabilization rather than metric gaming?**
    *   **Answer:** Yes, the move is technically justified as benchmark stabilization. Reports like `goal2911_scale_stable_canonical_perf_rows_2026-05-31.md` explicitly state the motivation: "Those rows are useful smoke tests, but they are not good benchmark gates for the project principle that benchmark apps should exercise meaningful RT/partner work." The objective was to make "measured work closer to the benchmark-app intent" and eliminate "microsecond jitter that dominated the smaller packet rows," rather than to artificially inflate performance metrics. This approach was further reinforced by the findings in `goal2907_hausdorff_repeat_stability_and_rtnn_near_parity_2026-05-31.md` and `goal2909_rtnn_repeat_stability_2026-05-31.md`, which highlighted measurement instability in short-row benchmarks.

2.  **Does the evidence support the statement "current internal v2.5 packet has no active performance targets"?**
    *   **Answer:** Yes, the evidence strongly supports this statement. Both the final report `docs/reports/goal2912_current_packet_scaled_defaults_2026-05-31.md` and its corresponding triage artifact `docs/reports/goal2912_current_packet_scaled_defaults_triage_2026-05-31.json` explicitly show `"performance_targets": []` and `"top_priority": null`, indicating no outstanding performance issues.

3.  **Does any code change add app-specific native engine logic or weaken the app-agnostic boundary?**
    *   **Answer:** No. All relevant reports (e.g., `goal2907`, `goal2909`, `goal2911`, `goal2912`) explicitly confirm: "No native engine code changed" and "No app-specific engine logic was added." The `src/rtdsl/v2_5_internal_readiness.py` also lists `"native_app_specific_engine_logic"` as a blocked action, reinforcing the commitment to maintaining an app-agnostic boundary.

4.  **Does the report language avoid overclaiming release readiness or public speedup claims?**
    *   **Answer:** Yes. The report language consistently avoids overclaiming. Every relevant report includes a "Boundary" section that explicitly disclaims "release consensus," "v2.5 release packet" status, and authorization for "public speedup claims," "broad RT-core claims," "whole-app speedup claims," "true-zero-copy claims," "automatic Triton selection," "package-install claims," or "paper-reproduction claims." The `src/rtdsl/v2_5_internal_readiness.py` further formalizes these boundaries.

5.  **What residual risks should remain tracked before any v2.5 release packet or public claim?**
    *   **Answer:** Based on the provided documentation, particularly `src/rtdsl/v2_5_internal_readiness.py`, the following residual risks and actions should be tracked:
        *   **Release Authorization:** The current packet is explicitly *not* a release authorization. Any release would require a new, dedicated process.
        *   **Public Claims:** No public speedup, broad RT-core, whole-app speedup, true zero-copy, package install, or paper reproduction claims are authorized.
        *   **Triton Integration:** Triton remains "visible but unpromoted" for Barnes-Hut vector sums, indicating that automatic Triton selection is not yet deemed stable or optimal.
        *   **Deferred Work:** The row/overlay continuation for Spatial RayJoin and the status of Tier C applications (Contact manifold, Robot collision) are explicitly noted as future work.
        *   **External Reviews:** Completion and satisfactory outcomes of outstanding external reviews (`V2_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PATHS`) are necessary.
        *   **Compiler Flag Alignment:** Tracking `goal2897_compiler_flag_alignment_before_release_packet` is necessary.
        *   **Multivendor/Second Arch Performance:** Tracking `goal2897_multivendor_or_second_arch_perf_check_before_release_packet` is critical for broader applicability.

## Required Verdict Format

`accept-with-boundary`
