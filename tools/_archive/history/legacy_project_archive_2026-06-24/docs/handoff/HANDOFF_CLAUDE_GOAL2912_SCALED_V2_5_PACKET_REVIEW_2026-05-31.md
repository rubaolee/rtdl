# Handoff: Claude Review of Goal2907-2912 v2.5 Performance Packet

Date: 2026-05-31
Requested reviewer: Claude
Expected output: `docs/reviews/goal2914_claude_review_goal2907_2912_scaled_v2_5_perf_packet_2026-05-31.md`

## Review Task

Please perform an independent read-only review of the recent v2.5 performance hardening chain from Goal2907 through Goal2912.

The main question: did the current source tree honestly move from noisy short-row performance targets to a clean, scale-stable internal v2.5 packet, without adding app-specific native engine logic or overclaiming release/public speedup readiness?

## Files To Read

Reports:

- `docs/reports/goal2906_current_packet_after_partner_selection_2026-05-31.md`
- `docs/reports/goal2907_hausdorff_repeat_stability_and_rtnn_near_parity_2026-05-31.md`
- `docs/reports/goal2908_current_packet_after_repeat9_2026-05-31.md`
- `docs/reports/goal2909_rtnn_repeat_stability_2026-05-31.md`
- `docs/reports/goal2911_scale_stable_canonical_perf_rows_2026-05-31.md`
- `docs/reports/goal2912_current_packet_scaled_defaults_2026-05-31.md`

Key artifacts:

- `docs/reports/goal2912_current_packet_scaled_defaults_pod/goal2855_summary.json`
- `docs/reports/goal2912_current_packet_scaled_defaults_triage_2026-05-31.json`
- `docs/reports/goal2911_scale_probe_pod/hausdorff_8192_repeat9.json`
- `docs/reports/goal2911_scale_probe_pod/rtnn_65536_repeat9.json`
- `docs/reports/goal2909_rtnn_repeat_stability_pod/clustered_ranked-summary-aggregate-prepared-query-float32.json`
- `docs/reports/goal2909_rtnn_repeat_stability_pod/clustered_cupy_grid.json`

Implementation/test files:

- `scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py`
- `scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py`
- `scripts/goal2902_v2_5_current_packet_perf_triage.py`
- `src/rtdsl/v2_5_internal_readiness.py`
- `tests/goal2912_current_packet_scaled_defaults_test.py`
- `tests/goal2911_scale_stable_canonical_perf_rows_test.py`
- `tests/goal2909_rtnn_repeat_stability_test.py`
- `tests/goal2907_hausdorff_repeat_stability_test.py`

## Facts To Verify

- Goal2912 packet is from commit `cf3a479d7f40c36df1b3f44f68de20ef1b098221`.
- Goal2912 packet summary is `all_pass: true`, `artifact_count: 7`, `source_dirty: []`, and `claim_boundary_violations: {}`.
- Goal2912 triage has `performance_targets: []` and `top_priority: null`.
- RTNN scaled defaults use `65,536` points and repeat `9`.
- Hausdorff scaled defaults use `8,192 x 8,192` points and repeat `9`.
- RTNN Goal2912 ratios are all green: uniform about `1.150x`, clustered about `2.522x`, shell about `7.640x` CuPy/RTDL.
- Hausdorff Goal2912 RTDL/CuPy ratio is about `0.940x`.
- RT-DBSCAN remains green at about `4.166x` to `4.857x` vs prepared CuPy grid.
- Barnes-Hut remains acceptable through measured partner selection: Torch selected, Triton visible but unpromoted, OptiX membership speedup about `154.306x`.
- The chain does not claim release readiness, public speedup, whole-app speedup, broad RT-core speedup, true zero-copy, package install, automatic Triton selection, or paper reproduction.

## Review Questions

1. Is the move from short-row 4K/32K defaults to 8K/65K defaults technically justified as benchmark stabilization rather than metric gaming?
2. Does the evidence support the statement "current internal v2.5 packet has no active performance targets"?
3. Does any code change add app-specific native engine logic or weaken the app-agnostic boundary?
4. Does the report language avoid overclaiming release readiness or public speedup claims?
5. What residual risks should remain tracked before any v2.5 release packet or public claim?

## Required Verdict Format

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

For this review, `accept-with-boundary` is expected if the packet is internally coherent but still not a release/public-claim authorization.

Please save the review to:

`docs/reviews/goal2914_claude_review_goal2907_2912_scaled_v2_5_perf_packet_2026-05-31.md`
