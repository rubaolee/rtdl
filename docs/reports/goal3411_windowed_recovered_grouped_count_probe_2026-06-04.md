# Goal3411 - Windowed Recovered Grouped Count Probe

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3410 identified the next safe step before a native paged stream ABI:
caller-visible Python window orchestration. Goal3411 implements and validates
that bridge on the full available `br_county.cdb`.

The probe partitions the left input into point windows, runs a bounded exact
device-column attempt per window, uses that window's explicit retry hint if it
overflows, runs grouped count on the recovered page, and merges page summaries
by key addition. The windows are caller-visible, but group keys are not assumed
to be disjoint.

## Evidence

Artifact:
`docs/reports/goal3411_windowed_recovered_grouped_count_probe_2026-06-04.json`

Pod: NVIDIA RTX A5000, driver 580.126.09

Source commit:
`8b1fe3082fb45fd708fbdaea64ad3dedf37e4ac4`

| Measure | Value |
| --- | ---: |
| Points | 16545 |
| Shapes | 15700 |
| Window size | 2048 |
| Windows | 9 |
| Initial max rows per window | 100 |
| Overflowed windows | 9 |
| Retried windows | 9 |
| Host exact rows | 47262 |
| Device grouped source rows | 47262 |
| Host groups | 16476 |
| Device groups | 16476 |
| Sum of per-window grouped rows | 16541 |
| Missing groups | 0 |
| Extra groups | 0 |
| Mismatched group values | 0 |

Representative windows:

| Window | Points | Required capacity | Device groups |
| --- | ---: | ---: | ---: |
| 0 | 2048 | 5666 | 2046 |
| 7 | 2048 | 6016 | 2048 |
| 8 | 161 | 352 | 161 |

## Interpretation

This proves a bounded Python orchestration bridge for cases where callers want
to cap individual exact-stream pages. It gives users a way to keep each page
small and explicit while preserving correct grouped summaries through key-based
summary addition.

It is still not the native graduation target. The native paged stream ABI would
need page cursors, page ownership/lifetime, and page-aware device continuations.

## Boundary

This does not implement native paged streams, device-only exact predicates,
automatic retry, hidden dispatch, true zero-copy, public speedup claims, RT-core
speedup claims, RayJoin reproduction claims, or release authorization.
