# Gemini Review: Goal2920-2921 HD RTN Stability

**Date:** 2026-06-01

**Reviewer:** Gemini Agent

**Verdict:** accept-with-boundary

## Executive Summary

This review assesses the stability risks associated with RTNN and Hausdorff scale, and the justification for changing the Hausdorff reduced target default to `4096`. It also verifies the cleanliness of the current seven-app packet after this change. The work successfully preserves the app-agnostic native-engine boundary and avoids overclaiming. Residual risks related to second-architecture, compiler fairness, RayJoin row/overlay, Tier C rows, and fresh 3-AI release review remain outside the scope of this review.

## Review Scope

This review covers the following files and associated goals:

*   `scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py`
*   `docs/reports/goal2920_rtnn_hausdorff_large_scale_stability_and_hd_default_2026-06-01.md`
*   `docs/reports/goal2920_hausdorff_rtnn_large_probe_pod/rtnn_262144_repeat9.json`
*   `docs/reports/goal2920_hausdorff_rtnn_large_probe_pod/hd_confirm/hd8192_target4096_repeat9.json`
*   `docs/reports/goal2920_hausdorff_rtnn_large_probe_pod/hd_confirm/hd16384_target4096_repeat9.json`
*   `docs/reports/goal2921_current_packet_after_hausdorff_target4096_2026-06-01.md`
*   `docs/reports/goal2921_current_packet_after_hd4096_pod/goal2855_summary.json`
*   `docs/reports/goal2921_current_packet_after_hd4096_pod/goal2921_triage.json`
*   `docs/reports/goal2921_current_packet_after_hd4096_pod/goal2801_hausdorff_xhd.json`
*   `tests/goal2920_rtnn_hausdorff_large_scale_stability_test.py`
*   `tests/goal2921_current_packet_after_hausdorff_target4096_test.py`
*   `src/rtdsl/v2_5_internal_readiness.py`

## Findings

### Goal2920: RTNN/Hausdorff Scale Stability

The provided evidence confirms the following:
*   The RTNN 262,144-point repeat-9 probe successfully passes.
*   RTNN CuPy/RTDL ratios are reported as uniform `3.740x`, clustered `1.971x`, and shell `4.342x`.
*   A regression was observed in the old Hausdorff 16k target-2048 repeat-9 row at `1.722x` RTDL/CuPy.
*   A target sweep identified `4096` as the optimal reduced target among those tested.
*   Confirmation passes for target `4096` repeat-9 show:
    *   8192 x 8192: RTDL/CuPy `0.949x`
    *   16384 x 16384: RTDL/CuPy `0.942x`
*   The code changes are limited to updating the canonical Hausdorff harness default to target `4096` and bumping the entrypoint version, without altering native engine logic.

### Goal2921: Current Packet After Hausdorff Target Change

The evidence demonstrates the following regarding the current seven-app packet:
*   The full seven-app packet passes at commit `fe628f4faec8e7d43521f11afd395b29462fba8b`.
*   `all_pass: true` is confirmed.
*   Artifact count is `7`, with dirty artifacts `{}` and claim-boundary violations `{}`.
*   The Hausdorff canonical row uses target `4096`, showing an exact match and RT cores, with an RTDL/CuPy ratio of `0.915x`.
*   Triage performance targets are `[]`.
*   The readiness index points to `docs/reports/goal2921_current_packet_after_hd4096_pod/goal2855_summary.json`.
*   Toolchain metadata remains present.

## Review Questions Addressed

1.  **Does Goal2920 correctly diagnose the RTNN and Hausdorff scale-stability risks?**
    Yes, Goal2920 correctly identifies and quantifies the scale-stability risks for RTNN and Hausdorff, particularly highlighting the regression in the old Hausdorff 16k target and the subsequent identification of `4096` as a more stable target.

2.  **Is changing the Hausdorff reduced target default to `4096` justified by the evidence?**
    Yes, the change is justified. The target sweep clearly shows `4096` as the best performing reduced target, and the confirmation passes for both 8192x8192 and 16384x16384 cases demonstrate improved RTDL/CuPy ratios near 0.95x, indicating better stability compared to the regressed `1.722x` of the old target.

3.  **Does Goal2921 prove the current seven-app packet is still clean after the default change?**
    Yes, Goal2921 provides strong evidence that the seven-app packet remains clean. The `all_pass: true`, zero dirty artifacts, and zero claim-boundary violations at the specified commit hash confirm the integrity of the packet post-change.

4.  **Does the work preserve the app-agnostic native-engine boundary?**
    Yes, the work preserves this boundary. The code changes are strictly limited to the Hausdorff harness default and entrypoint version bump, explicitly not altering native engine logic, as stated in the facts.

5.  **Does it avoid public/release/performance overclaiming?**
    Yes, the work avoids overclaiming. The changes are internal adjustments to improve stability and performance metrics, without introducing new public claims or performance guarantees beyond what the data supports.

6.  **What residual risks remain before any v2.5 release packet?**
    The handoff document explicitly states that the following residual risks remain outside the scope of this review and need to be addressed before a v2.5 release packet: second-architecture considerations, compiler fairness, RayJoin row/overlay, Tier C rows, and a fresh 3-AI release review.

## Conclusion

The work addresses the identified stability issues in RTNN and Hausdorff effectively by adjusting the default target to `4096`. The changes are well-justified by empirical evidence and do not negatively impact the existing application packet or the app-agnostic native-engine boundary. The work avoids overclaiming. However, the known out-of-scope items represent residual risks that must be considered for a comprehensive v2.5 release.
