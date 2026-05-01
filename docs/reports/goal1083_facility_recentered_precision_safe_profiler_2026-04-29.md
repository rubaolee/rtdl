# Goal1083 Facility Recentered Precision-Safe Profiler

Date: 2026-04-29

## Status

Implemented and locally validated.

## Problem

Goal1082 found that the original 2,500,000-copy facility RTX timing row is not
safe for public wording: the saved RTX row reports `8,898,102` threshold-reaching
queries, while the same-scale CPU oracle reports `10,000,000` covered customers.
The likely engineering cause is coordinate precision: the original generated
coordinates reach roughly 15 million on the x axis while the service radius is
`1.0`, which is unsafe for float-oriented RT traversal without a precision-aware
mapping.

## Change

Added `facility_service_coverage_recentered` to
`scripts/goal887_prepared_decision_phase_profiler.py`.

The new scenario:

- keeps the large query scale: 2,500,000 copies produce 10,000,000 query points;
- recenters each query to copy-local x coordinates before RT traversal;
- uses the canonical four depots from one tile as the build set;
- explicitly records `coordinate_mapping: copy_local_recentered_queries_canonical_depots`;
- limits the claim scope to recentered service-coverage decisions, not global-coordinate identity matching, ranked KNN, or facility-location optimization.

## Local Evidence

Generated:

`docs/reports/goal1083_facility_recentered_2_5m_cpu_oracle.json`

Key values:

- `scenario`: `facility_service_coverage_recentered`
- `copies`: `2,500,000`
- `customer_count`: `10,000,000`
- `covered_customer_count`: `10,000,000`
- `all_customers_covered`: `true`
- `coordinate_mapping`: `copy_local_recentered_queries_canonical_depots`
- `cpu_reference_total_sec`: `8.273853874998167`
- `input_build_sec`: `109.27930337400176`

## Next Cloud Command

Use this command on the next RTX pod:

```bash
PYTHONPATH=src:. python3 scripts/goal887_prepared_decision_phase_profiler.py \
  --scenario facility_service_coverage_recentered \
  --mode optix \
  --copies 2500000 \
  --iterations 5 \
  --radius 1.0 \
  --output-json docs/reports/goal1083_facility_recentered_2_5m_optix_validation.json
```

Do not use `--skip-validation` for this run. If validation is too expensive on
the pod, stop and add a reviewed validation-equivalent artifact instead of
publishing a speedup ratio.

## Boundary

Goal1083 prepares a precision-safe facility RTX validation candidate. It does
not authorize public RTX speedup wording, does not change release status, and
does not claim whole-app facility KNN acceleration.
