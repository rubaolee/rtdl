# Goal3406 - Recovered Exact Stream Grouped Count Probe

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3404 proved explicit retry recovers an overflowed exact device-column stream.
Goal3406 proves the recovered stream remains usable as input to the generic
compact grouped-count continuation.

The recovery remains caller-controlled: the first call overflows, the caller
reads `retry_capacity_hint`, the caller retries, and only then does the grouped
continuation run.

## Evidence

Artifact:
`docs/reports/goal3406_recovered_exact_stream_grouped_count_probe_2026-06-04.json`

Pod: NVIDIA RTX A5000, driver 580.126.09

Source commit:
`86d3aa1e5ba8855081077072e8d8bf10bd3d3d24`

| Stage | Value |
| --- | ---: |
| Initial max rows | 100 |
| Required capacity | 11316 |
| Retry capacity hint | 11316 |
| Recovered exact rows | 11316 |
| Host groups | 4094 |
| Device groups | 4094 |
| Grouped source rows | 11316 |
| Grouped output rows | 4094 |
| Missing groups | 0 |
| Extra groups | 0 |
| Mismatched group values | 0 |

The recovered exact stream was device-resident and the grouped-count output
matched host exact counts.

## Boundary

This proves explicit overflow recovery composes with an existing generic grouped
continuation. It does not implement automatic retry, chunked streaming overflow
recovery, a device-only exact predicate, true zero-copy, hidden dispatch, public
speedup claims, RT-core speedup claims, RayJoin reproduction claims, or release
authorization.
