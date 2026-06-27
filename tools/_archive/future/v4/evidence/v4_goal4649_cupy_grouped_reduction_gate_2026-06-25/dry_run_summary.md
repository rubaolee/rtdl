# V4 Goal4649 CuPy Grouped-Reduction Certification Gate

Status: `goal4649_cupy_gate_dry_run_no_claims`

CuPy performance remains unauthorized until Goal4649 completion review closes.
This file does not authorize public release, broad speedup, whole-app speedup,
POD spend, C ABI/embedding, arbitrary Numba callback support, or partner
migration/parity as V4 speed evidence.

## Ready Targets

| Candidate | Operator | Rows | Groups | Frozen speed floor |
|---|---|---:|---:|---:|
| cupy_grouped_reduction_device_columns_262144 | grouped_vector_sum_f64x2 | 262144 | 1024 | 1.2x |
| cupy_grouped_reduction_device_columns_524288 | grouped_vector_sum_f64x2 | 524288 | 2048 | 1.2x |

## Live Results

| Candidate | Rows | Groups | Representative speedup | Correctness parity | Host materialization in hot path | Pass |
|---|---:|---:|---:|---|---|---|
| none | 0 | 0 | 0.000x | false | false | false |

## Summary

```json
{
  "cupy_performance_claim_authorized": false,
  "live_rows_passed": 0,
  "mode": "dry_run",
  "ready_target_count": 2
}
```
