# Goal3396 - Exact Device Columns Grouped-Count Continuation

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3394 introduced exact closed-shape membership pair columns produced by the
OptiX native bridge. Goal3396 verifies that those exact device columns can feed
an existing generic grouped-count continuation without returning to app-specific
logic.

## Evidence

Artifact:
`docs/reports/goal3396_exact_device_columns_grouped_count_live_probe_2026-06-04.json`

Pod: NVIDIA RTX A5000, driver 580.126.09

Source commit:
`527ef4b69aa6a1b00e8e95e2c6d204549cba4cdd`

## Result

| Measure | Value |
| --- | ---: |
| Chains | 4096 |
| Shapes | 3762 |
| Exact device rows | 11316 |
| Exact relation row-count alias | 11316 |
| Host point groups | 4094 |
| Device point groups | 4094 |
| Missing groups | 0 |
| Extra groups | 0 |
| Mismatched group values | 0 |
| Grouped-count source rows | 11316 |
| Grouped-count output rows | 4094 |
| Grouped-count overflow | false |
| Reduction seconds | 0.00001969 |
| Compaction seconds | 0.000015124 |

The continuation path is:

```text
prepared.exact_device_columns(points)
  -> grouped_count_by_left_id_compact_device_columns(...)
  -> CuPy readback for test comparison only
```

## Boundary

This proves composition of generic exact relation columns with a generic grouped
count continuation. It does not authorize release, public speedup, RayJoin paper
reproduction, RTDL-beats-RayJoin, RT-core speedup, true-zero-copy, or native
default-route claims.

The exact row stream is still host-refined inside the native bridge. The future
performance target remains a device-only exact predicate or richer relation
witness stream.
