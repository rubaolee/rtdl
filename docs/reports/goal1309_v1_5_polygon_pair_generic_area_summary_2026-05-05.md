# Goal1309: Polygon Pair Generic Area Summary

Date: 2026-05-05

## Purpose

Goal1309 adds a generic v1.5 polygon exact-area summary wrapper for
`polygon_pair_overlap_area_rows / candidate_discovery_and_exact_area`.

This source migration has been pod-validated on OptiX. The inventory row is now
`pod_verified_generic`.

## Contract

The wrapper exposes:

```text
primitive = POLYGON_PAIR_EXACT_AREA_SUMMARY
summary primitive = REDUCE_FLOAT(SUM)
result layout = summary_float64_sums
dtype = float64
```

For the current integer-grid unit-cell workload, the wrapper also returns
`integer_parity_values`; these must match exactly before float tolerance is
considered.

## Implementation

Added:

```text
run_generic_polygon_pair_exact_area_summary()
```

The `embree` and `optix` summary paths now use this wrapper after candidate
pair discovery. Row output still uses the existing row materialization path.

## Boundary

- Candidate discovery remains separate from exact area summary.
- This is not a generic polygon overlay engine.
- This is not broad GIS acceleration.
- This does not authorize public NVIDIA speedup wording.

## Verification

Claude reviewed the Goal1308-1309 slice before pod promotion and returned
`ACCEPT` in:

```text
docs/reports/goal1309_claude_review_2026-05-05.md
```

Focused local gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1309_v1_5_polygon_pair_generic_area_summary_test \
  tests.goal1279_v1_4_polygon_pair_primitive_contract_test \
  tests.goal1308_v1_5_polygon_float_sum_contract_test
```
