# Handoff: Claude Review for Goals3556-3559 v2.9 Performance Cleanup

Date: 2026-06-06

## Task

Please perform a read-only external review of the v2.9 performance cleanup chain from Goals3556-3559 and write your review to:

`docs/reviews/goal3560_claude_review_goal3556_3559_v29_perf_cleanup_2026-06-06.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Context

The user asked for hard v2.9 performance work after being unhappy with weak v2.8/v2.3 rows. The current chain is:

- Goal3556: added RTNN `elapsed_median_sec` / min / max repeat scalars and moved current RTNN Goal2626 rows to median.
- Goal3557: fixed the v2.3 overlay so RTNN v2.3 also selects `elapsed_median_sec`; the corrected targeted A5000 row became `0.979578x`.
- Goal3558: refreshed the full 11-row A5000 packet after RTNN same-scalar cleanup.
- Goal3559: ran alternating RayDB count/sum probes after Goal3558 showed RayDB sum/count as the weakest one-run rows.

## Files To Read

Reports and artifacts:

- `docs/reports/goal3556_rtnn_median_repeat_metric_hardening_2026-06-06.md`
- `docs/reports/goal3556_rtnn_probe_a5000/summary.json`
- `docs/reports/goal3557_rtnn_same_scalar_median_metric_a5000_2026-06-06.md`
- `docs/reports/goal3557_rtnn_same_scalar_median_metric_a5000/summary.json`
- `docs/reports/goal3558_v2_9_full_packet_after_rtnn_same_scalar_2026-06-06.md`
- `docs/reports/goal3558_v2_9_full_packet_after_rtnn_same_scalar_a5000_cap250k/summary.json`
- `docs/reports/goal3559_raydb_sum_count_stability_probe_2026-06-06.md`
- `docs/reports/goal3559_raydb_sum_count_probe_a5000/summary.json`

Code/tests:

- `scripts/goal2348_rtnn_v2_2_external_runner.py`
- `scripts/goal2626_benchmark_embree_optix_baseline.py`
- `docs/patches/goal3547_v23_measurement_overlay_repeat_hooks_2026-06-06.patch`
- `tests/goal3556_rtnn_median_repeat_metric_hardening_test.py`
- `tests/goal3557_rtnn_same_scalar_median_metric_a5000_test.py`
- `tests/goal3558_v2_9_full_packet_after_rtnn_same_scalar_test.py`
- `tests/goal3559_raydb_sum_count_stability_probe_test.py`

## Review Questions

1. Did Goal3556 correctly preserve RTNN compatibility while adding median/min/max repeat scalars?
2. Did Goal3557 correctly fix the v2.3 overlay mismatch so RTNN uses the same scalar on both sides?
3. Is Goal3558's full packet interpretation honest: target-compliant, internal only, geomean positive, but not a public speedup/release claim?
4. Does Goal3559 reasonably de-escalate RayDB sum/count from "code regression" to "near-parity / one-run variance"?
5. Are any claim boundaries, release boundaries, RT-core claims, zero-copy claims, or paper-reproduction claims over-authorized?
6. What should be required before treating the v2.9 performance packet as a stable internal closeout?

## Expected Review Shape

Lead with findings by severity. Include exact file references and line numbers where practical. Then provide a concise verdict and required-before-next-step items. Do not modify source files except to write the requested review.
