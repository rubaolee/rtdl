# Goal2791 Gemini Review - Thresholded Partner Selection Guidance

**Date:** 2026-05-31

**Review Goal:** Review Goal2791, which converts Goal2790's mixed tiled Hausdorff evidence into machine-readable thresholded partner-selection guidance.

## Files Inspected:

- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `tests/goal2791_thresholded_partner_selection_guidance_test.py`
- `tests/goal2782_v2_5_partner_selection_guidance_test.py`
- `tests/goal2783_v2_5_app_migration_selection_guidance_test.py`
- `docs/reports/goal2791_thresholded_partner_selection_guidance_2026-05-31.md`
- `docs/reports/goal2790_pod_artifacts/goal2790_tiled_dense_point_nearest_hausdorff_pod_69_30_85_171_2026-05-31.json`
- `docs/reports/goal2791_pod_artifacts/goal2791_hausdorff_32k_tiled_probe_pod_69_30_85_171_2026-05-31.json`

## Answers to Questions:

1.  **Does the new `measured_mixed_preview_guidance` row accurately encode the Goal2790 crossover without turning it into hidden auto-dispatch?**

    Yes. The `V25PartnerConditionalGuidanceRow` type, used for the `dense_exact_hausdorff_tiled_nearest_then_global_max` operation, accurately encodes the Goal2790 crossover. The `measured_partner_over_comparison_min_ratio` is 0.745 (Triton faster) and `measured_partner_over_comparison_max_ratio` is 19.61 (Triton slower), clearly showing mixed performance. The `measured_partner_faster_shape_count` is 1, and `measured_partner_slower_shape_count` is 3, further detailing the crossover. Crucially, the `auto_select_measured_partner_allowed` field is explicitly `False` in this row, and the overall `v2_5_partner_selection_guidance()` function also sets `auto_select_preview_partner_allowed: False`. This prevents any hidden auto-dispatch based on this mixed evidence. The associated recommendation also explicitly states "Do not auto-select" and "thresholded preview evidence," reinforcing this boundary.

2.  **Does the Hausdorff/X-HD migration plan correctly preserve two negative rows plus one thresholded row, with auto-selection blocked?**

    Yes. The `hausdorff_xhd` entry in `V2_5_TRITON_BENCHMARK_APP_PLANS` correctly integrates the three relevant guidance rows:
    *   Two rows for `dense_exact_hausdorff_argmin_argmax` (Goal2787) and `dense_exact_hausdorff_nearest_then_global_max` (Goal2788) are categorized as `measured_negative_preview_guidance`.
    *   One row for `dense_exact_hausdorff_tiled_nearest_then_global_max` (Goal2790) is categorized as `measured_mixed_preview_guidance`.
    The `measured_negative_preview_guidance_count` is 2, and `measured_mixed_preview_guidance_count` is 1 for the `hausdorff_xhd` app. The `auto_select_preview_partner_allowed` is explicitly `False` at the app plan level, and the `first_port_action` notes reinforce that auto-selection is blocked for this application.

3.  **Does the 32K pod artifact support only bounded tiled-completion evidence, not a same-contract Torch speedup claim?**

    Yes. The `goal2791_hausdorff_32k_tiled_probe_pod_69_30_85_171_2026-05-31.json` artifact clearly indicates that the Torch dense baseline OOMed at 32K (`"status": "not_rerun_after_prior_oom"`). Therefore, no same-contract Torch speedup claim can be made at this scale. The artifact successfully records bounded tiled-completion evidence for the Triton tiled path, with several block sizes reporting `status: "ok"` and consistent distance error. Furthermore, the `claim_boundary` within the artifact explicitly sets all speedup and release claims to `false`.

4.  **Are public speedup, RT-core speedup, whole-app speedup, true-zero-copy, and v2.5 release claims still blocked?**

    Yes. All these claims remain consistently blocked across all inspected files.
    *   `src/rtdsl/v2_5_partner_selection_guidance.py`: The `V2_5_PARTNER_SELECTION_GUIDANCE_CLAIM_BOUNDARY` explicitly lists these as unauthorized. Both `V25PartnerSelectionGuidanceRow` and `V25PartnerConditionalGuidanceRow` dataclasses enforce that corresponding boolean flags for these claims are `False`.
    *   `src/rtdsl/v2_5_triton_app_migration.py`: The `v2_5_triton_benchmark_app_migration_plan()` function and the `V25TritonBenchmarkAppPlan` dataclass explicitly set these flags to `False`.
    *   Pod artifacts (`goal2790_tiled_dense_point_nearest_hausdorff_pod_69_30_85_171_2026-05-31.json` and `goal2791_hausdorff_32k_tiled_probe_pod_69_30_85_171_2026-05-31.json`): The `claim_boundary` sections within these JSON artifacts consistently set these claims to `false`.
    *   Test files: Tests like `test_tiled_hausdorff_guidance_is_mixed_and_claim_safe` explicitly assert that these flags are `False` for the relevant guidance rows.

## Verdict:

`accept-with-boundary`
