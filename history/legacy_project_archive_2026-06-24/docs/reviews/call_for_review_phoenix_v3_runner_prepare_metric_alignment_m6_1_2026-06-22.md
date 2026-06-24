# Call For Review: Phoenix V3 Runner Prepare Metric Alignment M6.1

Date: 2026-06-22
Requested reviewer: fallback AI if Claude/Gemini remain blocked

## Review Packet

Please review:

- `docs/reports/phoenix_v3_runner_prepare_metric_alignment_m6_1_2026-06-22.md`
- `docs/reports/phoenix_v3_runner_metadata_overhead_reduction_m6_2026-06-22.md`
- `docs/reviews/kepler_phoenix_v3_runner_metadata_overhead_reduction_m6_fallback_review_2026-06-22.md`

Code touched:

- `src/rtdsl/prepared_execution.py`
- `examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
- `scripts/v3_phoenix_hausdorff_threshold_runner_pod_ab.py`

## Questions

Return one verdict:

- `accept_for_focused_hausdorff_m5_pod_no_regression_validation`
- `accept_local_only_need_query_path_work_before_pod`
- `reject_metric_alignment_hides_runner_cost`
- `reject_breaks_claim_boundaries_or_scope`

Please answer:

1. Is recording both native prepare and outer runner prepare/cache timing a
   valid generic runner improvement?
2. Does using `legacy_aligned_prepare_sec` for Hausdorff phase-total make the
   runner-vs-legacy canary fairer, or does it hide important runner cost?
3. Is wrapper wall still enough to keep end-to-end runner tax visible?
4. Is one focused Hausdorff M5 pod rerun justified now?
5. What exact pass/fail classification should be used?

## Non-Authorization

This review cannot authorize V3 release, all-app rerun, public speedup wording,
broad V3-over-V2 wording, whole-app claims, true-zero-copy claims, or V4 /
external-buffer wording.
