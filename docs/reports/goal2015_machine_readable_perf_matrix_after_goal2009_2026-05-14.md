# Goal2015 Machine-Readable Perf Matrix After Goal2009

Date: 2026-05-14

Status: json-refresh-complete-external-review-needed

## Summary

Goal2015 creates the machine-readable successor requested by Goal2014:

`docs/reports/goal2015_current_all_app_v18_v2_perf_analysis_after_goal2009_2026-05-14.json`

The file starts from Goal1931's all-app JSON and changes only the current
road-hazard row to use Goal2009's A5000 pod artifact:

`docs/reports/goal2009_pod_smoke/road_hazard_prepared_cupy_cached_triangle_lookup_4096.json`

## Updated Row

`road_hazard_screening` now records:

- `artifact: docs/reports/goal2009_pod_smoke/road_hazard_prepared_cupy_cached_triangle_lookup_4096.json`
- `claim_class: implemented-prepared-cupy-exact-filter`
- `matrix_state: implemented-and-pod-timed-current-goal2009`
- `partner: cupy`
- `size: 4096`
- `v18_prepared_s: 0.009691450744867325`
- `v2_prepared_partner_s: 0.00393231026828289`
- `ratio_vs_v18_prepared: 0.4057504259994795`

This is a `2.46x` speedup versus the v1.8 prepared native row for the
same-contract prepared road-hazard priority-flag output.

## Boundary

The JSON retains:

- `v2_0_release_authorized: false`
- `whole_app_speedup_claim_authorized: false`
- `control_rows_are_speedup_evidence: false`

It also adds:

- `road_hazard_row_refreshed_after_goal2009: true`

The refresh is intentionally narrow. It does not reclassify the other 15 rows
or authorize a final v2.0 release claim.
