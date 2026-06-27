# Goal666: Mac Visibility Count Performance

Date: 2026-04-20

Status: characterization artifact

## Methodology

- Workload: Visibility/collision blocked-ray count.
- Correctness mode: `backend_agreement`.
- Apple RT uses prepared scene and prepacked rays, then returns only blocked-ray count. Embree/Shapely baselines materialize rows and reduce to count because they do not expose the same scalar prepared-count API in this harness.
- Each timing sample loops enough calls to approach the requested target duration, then reports per-query median.
- This is a fair app-level comparison for scalar blocked-ray count, not for full row-table output.

## Host

```json
{
  "apple_rt_context": "Apple M4",
  "apple_rt_version": "(0, 9, 3)",
  "embree_version": "(4, 4, 0)",
  "hostname": "Rs-MacBook-Air.local",
  "platform": "macOS-26.3-arm64-arm-64bit-Mach-O",
  "processor": "arm",
  "python": "3.14.0",
  "sw_vers": "ProductName:\t\tmacOS\nProductVersion:\t\t26.3\nBuildVersion:\t\t25D125"
}
```

## Results

### Setup Costs

| Case | Apple RT Scene Prepare | Apple RT Ray Pack | Oracle Time |
| --- | ---: | ---: | ---: |
| dense_blocked:large_count | 0.075947 s | 0.014594 s | n/a |
| mixed_visibility:large_count | 0.027678 s | 0.014007 s | n/a |
| sparse_clear:large_count | 0.027287 s | 0.013420 s | n/a |

### Repeated Query Cost

| Case | Rays | Triangles | Backend | Status | Per-Query Median | Inner Iterations | Blocked Count | Correctness |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: | --- |
| dense_blocked:large_count | 32768 | 8192 | `apple_rt_prepared_packed_count` | ok | 0.001330064 s | 2252 | 32768 | apple_rt_prepared_packed_count=True |
| dense_blocked:large_count | 32768 | 8192 | `embree_row_count` | ok | 0.015297282 s | 103 | 32768 | apple_rt_prepared_packed_count=True |
| dense_blocked:large_count | 32768 | 8192 | `shapely_strtree_count` | ok | 0.297816304 s | 7 | 32768 | apple_rt_prepared_packed_count=True |
| mixed_visibility:large_count | 32768 | 8192 | `apple_rt_prepared_packed_count` | ok | 0.001182773 s | 2143 | 16384 | apple_rt_prepared_packed_count=True |
| mixed_visibility:large_count | 32768 | 8192 | `embree_row_count` | ok | 0.015251223 s | 133 | 16384 | apple_rt_prepared_packed_count=True |
| mixed_visibility:large_count | 32768 | 8192 | `shapely_strtree_count` | ok | 0.252873766 s | 8 | 16384 | apple_rt_prepared_packed_count=True |
| sparse_clear:large_count | 32768 | 8192 | `apple_rt_prepared_packed_count` | ok | 0.000910397 s | 3096 | 0 | apple_rt_prepared_packed_count=True |
| sparse_clear:large_count | 32768 | 8192 | `embree_row_count` | ok | 0.014742673 s | 139 | 0 | apple_rt_prepared_packed_count=True |
| sparse_clear:large_count | 32768 | 8192 | `shapely_strtree_count` | ok | 0.196451636 s | 11 | 0 | apple_rt_prepared_packed_count=True |

## Ratio Summary

- `dense_blocked:large_count`: Apple packed-count / Embree row-count: 0.087x; Apple packed-count / Shapely count: 0.004x
- `mixed_visibility:large_count`: Apple packed-count / Embree row-count: 0.078x; Apple packed-count / Shapely count: 0.005x
- `sparse_clear:large_count`: Apple packed-count / Embree row-count: 0.062x; Apple packed-count / Shapely count: 0.005x

## Major Conclusion

For scalar visibility/collision count, the optimized Apple RT prepared packed-count path is now substantially faster than row-materialized Embree and Shapely/GEOS in this harness. This does not mean Apple RT is faster for full emitted-row output: the row path remains slower than Embree because Python-facing row materialization dominates. The correct claim is narrower: when an app can prepack rays and consume a scalar count, Apple RT can expose a fast Mac hardware-backed path.

## Interpretation Rules

- Include Apple RT scene preparation and ray packing separately when judging first-query latency.
- Use per-query timing for repeated-query apps where obstacles and ray buffers are reused.
- Do not compare this scalar-count result against full-row Embree as if the output contracts were identical.
- Do not generalize this result to Apple RT DB or graph workloads.
