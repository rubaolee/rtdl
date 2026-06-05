# Goal3408 - Full br_county Recovered Exact Stream Grouped Count

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3406 proved explicit overflow recovery plus grouped-count continuation on a
4096-chain slice. Goal3408 repeats the same path on the full available
`br_county.cdb` dataset.

The artifact intentionally uses the Goal3406 probe schema because this is the
same probe run at full dataset scale.

## Evidence

Artifact:
`docs/reports/goal3408_full_br_county_recovered_exact_stream_grouped_count_2026-06-04.json`

Pod: NVIDIA RTX A5000, driver 580.126.09

Source commit:
`67da88268767b0b2005573243056f4804d2b830e`

| Measure | Value |
| --- | ---: |
| Points | 16545 |
| Shapes | 15700 |
| Initial max rows | 100 |
| Required capacity | 47262 |
| Retry capacity hint | 47262 |
| Recovered exact rows | 47262 |
| Host groups | 16476 |
| Device groups | 16476 |
| Grouped source rows | 47262 |
| Grouped output rows | 16476 |
| Missing groups | 0 |
| Extra groups | 0 |
| Mismatched group values | 0 |

The recovered exact stream was device-resident and the grouped-count output
matched host exact counts over the full available CDB.

## Boundary

This is full-scale evidence for explicit overflow recovery composing with an
existing generic grouped continuation. It does not implement automatic retry,
chunked streaming overflow recovery, a device-only exact predicate, true
zero-copy, hidden dispatch, public speedup claims, RT-core speedup claims,
RayJoin reproduction claims, or release authorization.
