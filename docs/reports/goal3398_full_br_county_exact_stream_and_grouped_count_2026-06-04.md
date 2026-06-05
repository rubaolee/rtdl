# Goal3398 - Full br_county Exact Stream And Grouped Count

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3394 and Goal3396 validated the exact device-column bridge and grouped-count
continuation on a 4096-chain slice. Goal3398 runs the same two paths on the full available `br_county.cdb` dataset.

## Evidence

Artifacts:

- `docs/reports/goal3398_full_br_county_exact_device_columns_2026-06-04.json`
- `docs/reports/goal3398_full_br_county_exact_grouped_count_2026-06-04.json`

Pod: NVIDIA RTX A5000, driver 580.126.09

Source commit:
`8bdc8a647bc4e126d43f7eeccc71d774f156a00d`

## Exact Device Columns

| Measure | Value |
| --- | ---: |
| Points | 16545 |
| Shapes | 15700 |
| Exact rows | 47262 |
| Device-column rows | 47262 |
| Exact relation row-count alias | 47262 |
| Missing exact pairs | 0 |
| Extra pairs | 0 |
| Device resident | true |
| Overflow | false |

## Grouped Count Continuation

| Measure | Value |
| --- | ---: |
| Exact device rows | 47262 |
| Host point groups | 16476 |
| Device point groups | 16476 |
| Missing groups | 0 |
| Extra groups | 0 |
| Mismatched group values | 0 |
| Grouped-count source rows | 47262 |
| Grouped-count output rows | 16476 |
| Grouped-count overflow | false |

## Interpretation

The exact stream bridge and grouped-count continuation both scale to the full
available `br_county` CDB dataset. This closes the chain-offset gap that remained
after the 512/1024/2048 nested slices and the 4096 negative probe.

This is still a bridge: exact membership is host-refined inside the native
backend, then exact ids are uploaded into native-owned CUDA columns. The future
performance target remains a device-only exact predicate or richer relation
witness stream.

## Boundary

This does not authorize release, public speedup, RayJoin paper reproduction,
RTDL-beats-RayJoin, RT-core speedup, true-zero-copy, or native default-route
claims.
