# Handoff: Gemini Review For Goal3990 Dense Fixed-Radius Grouped Union

Please perform an independent read-only review of the Goal3990 design packet.

## Files To Read

- `docs/reports/goal3990_dense_fixed_radius_grouped_union_design_2026-06-08.md`
- `docs/reports/goal3989_rt_dbscan_grouped_union_telemetry_2026-06-08.md`
- `tests/goal3990_dense_fixed_radius_grouped_union_design_test.py`
- `docs/research/future_version_to_do_list.md`

## Review Questions

1. Does Goal3990 correctly infer from Goals3987-3989 that existing route toggles and partner substitution are exhausted for the measured RT-DBSCAN profile?
2. Is the proposed primitive boundary app-agnostic, with DBSCAN/clustering policy kept outside native ABI and native implementation vocabulary?
3. Are the acceptance criteria strong enough before native ABI changes: deterministic component-root policy, staleness/convergence metadata, parity tests, dense/sparse pod evidence, claim-boundary discipline, and external review?
4. Does the report avoid overclaiming release readiness, broad RT-core speedup, whole-app speedup, true-zero-copy, paper reproduction, automatic backend/partner selection, or app-specific engine logic?
5. Are there missing risks or better implementation directions for a generic dense fixed-radius grouped-union continuation?

## Required Output

Write the review to:

`docs/reviews/goal3991_gemini_review_goal3990_dense_grouped_union_design_2026-06-08.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

