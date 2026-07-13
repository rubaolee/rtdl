# Goal5230 - ModelNet40 All-2000 Paper-Log Record Coverage Result

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_all2000_record_value_coverage_from_all400_unique_pairs
```

Goal5230 proves ModelNet40 paper-log **HDResult value coverage** for all 2000
ModelNet40 records by combining:

```text
Goal5229 all-400 unique-pair route result: 400 / 400 matched at 1e-6
paper-log duplicate equivalence: each unique pair has five value-identical records
```

This does **not** mean all 2000 records were individually rerun through RTDL.
It also does not reproduce per-algorithm performance. It proves that every
paper-log ModelNet40 record's HDResult value is covered by a matched unique-pair
RTDL result.

## Evidence

Record coverage summary:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5230_modelnet40_all2000_record_coverage_summary_2026-07-09.json
```

Source unique-pair summary:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5229_modelnet40_all400_float32norm_aggregate_summary_2026-07-09.json
```

## Result

```text
record_count = 2000
unique_pair_count = 400
covered_record_count = 2000
all_records_covered = true
duplicate_count_distribution = {"5": 400}
duplicate_signature_mismatch_count = 0
missing_unique_pair_count = 0
unmatched_unique_pair_count = 0
```

Algorithm distribution across the 2000 paper-log records:

```text
Early Break = 400
Hybrid = 1200
Ray Tracing = 400
```

Every unique pair has paper-log records from:

```text
Early Break + Hybrid + Ray Tracing
```

The value signature used for duplicate equivalence includes:

```text
HDResult
normalize flag
translate value
input type
input point counts
num_points_per_cell
max_hit
```

It intentionally does **not** require Algorithm to be the same, because the
paper logs contain multiple algorithm records for the same input pair. The
coverage claim is therefore HDResult value coverage, not per-algorithm
execution/performance coverage.

## Implementation

Added app-owned helper:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_modelnet40_record_coverage.py
```

Tests:

```text
tests/goal5230_modelnet40_record_coverage_test.py
```

Validation:

```text
py -m unittest tests.goal5230_modelnet40_record_coverage_test tests.goal5219_xhd_off_normalize_input_contract_test tests.goal5223_modelnet40_algorithm_aware_comparator_test
Ran 21 tests OK

POD:
python3 -m unittest tests.goal5230_modelnet40_record_coverage_test
Ran 5 tests OK
```

## Claim Boundary

Allowed:

```text
All 2000 ModelNet40 paper-log records are covered for HDResult value by the
400/400 unique-pair RTDL result plus duplicate-record equivalence.
```

Forbidden:

```text
All 2000 records were individually rerun through RTDL.
Per-algorithm performance is reproduced.
Exact paper input byte identity is proved.
Author-vs-RTDL performance parity is established.
Full X-HD paper reproduction is complete.
```

## Next Step

The next evidence target should be either:

```text
1. denominator-aligned ModelNet40 performance matrix, or
2. another paper workload family beyond ModelNet40.
```

Performance claims remain unauthorized until a fair matrix aligns:

```text
author algorithm / RTDL route
input provenance
normalization semantics
process wall vs internal AvgTime vs route wall
hardware
warm/cold regime
```
