# Goal3400 - Exact Device Columns Overflow Probe

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3394 introduced exact membership device columns. Goal3400 verifies the
fail-closed behavior when the caller supplies an insufficient `max_rows`
capacity.

## Evidence

Artifact:
`docs/reports/goal3400_exact_device_columns_overflow_probe_2026-06-04.json`

Pod: NVIDIA RTX A5000, driver 580.126.09

Source commit:
`3b09c58ab9750df289f4991437803bd67f8f5a53`

## Result

| Measure | Value |
| --- | ---: |
| Points | 4096 |
| Shapes | 3762 |
| Requested max rows | 100 |
| Exact relation row count | 11316 |
| Output row count | 0 |
| Overflow | true |
| Device resident | false |
| CuPy wrap raised | true |

The CuPy wrapper refuses to expose overflowed columns:

```text
cannot wrap an overflowed device pair-column stream
```

## Boundary

This proves fail-closed overflow behavior for the exact-device-column bridge. It
does not provide a streaming overflow recovery path yet.

This does not authorize release, public speedup, RayJoin paper reproduction,
RTDL-beats-RayJoin, RT-core speedup, true-zero-copy, or native default-route
claims.
