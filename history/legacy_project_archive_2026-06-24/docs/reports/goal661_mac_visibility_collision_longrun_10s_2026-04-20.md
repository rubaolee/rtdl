# Goal661: Mac Visibility/Collision Long-Run 10s Performance

Date: 2026-04-20

Status: long-run characterization artifact

## Methodology

- Reported engines: Apple RT one-shot, Apple RT prepared-query, Embree, Shapely/GEOS STRtree when installed.
- CPU/oracle is used only for correctness parity and is not reported as a performance engine.
- Each case reports repeated warm samples; with target-sample mode, each sample loops enough queries to approach the requested wall time and also reports per-query median.
- Apple RT uses `run_apple_rt(..., native_only=True)` over the 2D any-hit kernel.

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

| Case | Rays | Triangles | Backend | Status | Sample Median | Per-Query Median | Inner Iterations | Prepare | Blocked | Matches Oracle |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| dense_blocked:long_10s | 8192 | 2048 | `apple_rt_prepared_query` | ok | 8.368069 s | 0.037357453 s | 224 | 0.051323 s | 8192 | True |
| dense_blocked:long_10s | 8192 | 2048 | `embree` | ok | 10.559871 s | 0.003521131 s | 2999 | n/a | 8192 | True |
| dense_blocked:long_10s | 8192 | 2048 | `shapely_strtree` | ok | 10.150426 s | 0.073553813 s | 138 | n/a | 8192 | True |
| sparse_clear:long_10s | 8192 | 2048 | `apple_rt_prepared_query` | ok | 9.126244 s | 0.021677539 s | 421 | 0.013649 s | 0 | True |
| sparse_clear:long_10s | 8192 | 2048 | `embree` | ok | 10.819078 s | 0.003368331 s | 3212 | n/a | 0 | True |
| sparse_clear:long_10s | 8192 | 2048 | `shapely_strtree` | ok | 10.124546 s | 0.047983628 s | 211 | n/a | 0 | True |

## Ratio Summary

- `dense_blocked:long_10s`: Apple RT prepared-query / Embree per-query: 10.610x; Apple RT prepared-query / Shapely STRtree per-query: 0.508x
- `sparse_clear:long_10s`: Apple RT prepared-query / Embree per-query: 6.436x; Apple RT prepared-query / Shapely STRtree per-query: 0.452x

## Major Conclusion

This is a useful Mac real-hardware app benchmark, but the current Apple RT path is not yet performance-leading versus Embree. All reported Apple RT, Embree, and Shapely/GEOS rows pass correctness parity on the measured scales. Embree is the fastest engine in this run. Prepared Apple RT separates obstacle setup from repeated ray queries; use that row to judge app-style repeated-query behavior.

## Interpretation Rules

- Do not treat CPU/oracle as a reported competitor in this benchmark.
- Treat Shapely absence as an environment gap, not an RTDL speed result.
- Treat Apple RT results as Mac real-hardware evidence only for the Apple RT rows that pass parity.
- Dense-blocked cases are the intended any-hit-friendly shape; sparse-clear cases expose worst-case traversal/setup behavior.
