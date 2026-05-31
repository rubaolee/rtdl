# Handoff - Gemini Review For Goal2791

Please write an independent Gemini review to:

`docs/reviews/goal2791_gemini_review_thresholded_partner_selection_guidance_2026-05-31.md`

Review Goal2791, which converts Goal2790's mixed tiled Hausdorff evidence into
machine-readable thresholded partner-selection guidance.

Files to inspect:

- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `tests/goal2791_thresholded_partner_selection_guidance_test.py`
- `tests/goal2782_v2_5_partner_selection_guidance_test.py`
- `tests/goal2783_v2_5_app_migration_selection_guidance_test.py`
- `docs/reports/goal2791_thresholded_partner_selection_guidance_2026-05-31.md`
- `docs/reports/goal2790_pod_artifacts/goal2790_tiled_dense_point_nearest_hausdorff_pod_69_30_85_171_2026-05-31.json`
- `docs/reports/goal2791_pod_artifacts/goal2791_hausdorff_32k_tiled_probe_pod_69_30_85_171_2026-05-31.json`

Questions to answer:

1. Does the new `measured_mixed_preview_guidance` row accurately encode the
   Goal2790 crossover without turning it into hidden auto-dispatch?
2. Does the Hausdorff/X-HD migration plan correctly preserve two negative rows
   plus one thresholded row, with auto-selection blocked?
3. Does the 32K pod artifact support only bounded tiled-completion evidence,
   not a same-contract Torch speedup claim?
4. Are public speedup, RT-core speedup, whole-app speedup, true-zero-copy, and
   v2.5 release claims still blocked?

Use one of these verdicts exactly:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`
