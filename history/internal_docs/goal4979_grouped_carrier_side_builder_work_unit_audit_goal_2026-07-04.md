# Goal4979: Grouped Carrier Side-Builder Work-Unit Audit

Date: 2026-07-04

## Purpose

Goal4978 showed that grouped carrier construction is dominated by the side-builder Numba loop:

- side0 builder: 0.576031s
- side1 builder: 0.067711s
- carrier total: 0.654825s

Goal4979 audits the side-builder work units before any optimization. The goal is to determine whether side0 is dominated by original chain-point scanning, intersection-run transitions, emitted/skipped groups, or dedupe append work.

## Work

Add app-owned metrics to the compiled side-builder:

- chain count
- chain points scanned
- edge slots scanned
- intersection run count
- intersection row count
- intersection display-point appends
- dedupe append calls
- split flush count
- chain final flush count
- kept group count
- skipped group count
- emitted point-row count
- sorted intersection order count
- run-start count

Expose these metrics in `grouped_carrier.side_work_metrics` and `grouped_carrier.side_work_metrics_total`.

## Verification

Run the same top4 route:

```text
--device-columnar
--compiled-group
--bounded-exact-lsi-device-columns --bounded-exact-lsi-capacity 600000
--point-location-device-face-columns
--fast-scaled-point-pack
```

The result must answer:

1. Why is side0 much slower than side1?
2. Is side0 time proportional to chain points, intersection rows, group emissions, skipped groups, or dedupe append calls?
3. Does instrumentation preserve structural anchors from Goal4978?
4. What is the next concrete optimization, if any?

## Boundary

Allowed:

- app-owned instrumentation only
- no core/native changes
- no new performance headline

Forbidden:

- no RayJoin-specific RTDL core primitive
- no grouped-carrier core promotion
- no Layer 4 fusion
- no author-performance claim

## Exit Labels

- `completed_side_builder_chain_scan_dominated`
- `completed_side_builder_intersection_run_dominated`
- `completed_side_builder_group_emission_dominated`
- `completed_side_builder_mixed_no_single_target`
- `fail_redo_due_to_missing_work_unit_evidence`
