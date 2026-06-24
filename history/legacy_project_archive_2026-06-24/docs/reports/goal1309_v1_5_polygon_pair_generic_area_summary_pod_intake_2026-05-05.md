# Goal1309 Pod Intake: Polygon Pair Generic Area Summary

Date: 2026-05-05

## Source

Goal1309 validates `polygon_pair_overlap_area_rows /
candidate_discovery_and_exact_area` on the RTX pod after routing the summary
path through `run_generic_polygon_pair_exact_area_summary()`.

Pod workspace:

```text
/workspace/rtdl_goal1292
```

The Goal1308-1309 source slice was copied into the pod workspace before
testing.

## Evidence

Compact copied artifact:

```text
docs/reports/goal1309_v1_5_polygon_pair_generic_area_summary_pod_results/compact_summary.json
```

Command shape:

```text
PYTHONPATH=src:. python3 examples/rtdl_polygon_pair_overlap_area_rows.py \
  --backend optix \
  --copies 256 \
  --output-mode summary \
  --require-rt-core
```

Result:

| Field | Value |
| --- | --- |
| App | `polygon_pair_overlap_area_rows` |
| Backend | `optix` |
| Copies | 256 |
| Backend mode | `optix_native_assisted` |
| Candidate rows | 512 |
| Generic primitive | `POLYGON_PAIR_EXACT_AREA_SUMMARY` |
| Summary primitive | `REDUCE_FLOAT(SUM)` |
| Result layout | `summary_float64_sums` |
| Dtype | `float64` |
| Integer parity values | overlap pairs 512, intersection area 1280, union area 4864 |

The app summary exactly matched the generic wrapper integer parity values.

## Status

`polygon_pair_overlap_area_rows / candidate_discovery_and_exact_area` is now
pod-verified as a generic v1.5 polygon exact-area summary row.

Claude reviewed the Goal1308-1309 source slice before pod promotion and
returned `ACCEPT` with no blocking issues in:

```text
docs/reports/goal1309_claude_review_2026-05-05.md
```

This remains an exact subpath claim only. It does not claim a generic polygon
overlay engine, broad GIS acceleration, whole-app speedup, or public NVIDIA
speedup wording.

## Pod Tests

Passed on pod:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1309_v1_5_polygon_pair_generic_area_summary_test \
  tests.goal1279_v1_4_polygon_pair_primitive_contract_test \
  tests.goal1308_v1_5_polygon_float_sum_contract_test
```

Result: 11 tests OK.
