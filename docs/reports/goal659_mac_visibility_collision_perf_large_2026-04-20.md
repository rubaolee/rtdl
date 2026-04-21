# Goal659: Mac Visibility/Collision Performance

Date: 2026-04-20

Status: characterization artifact

## Methodology

- Reported engines: Apple RT one-shot, Apple RT prepared-query, Embree, Shapely/GEOS STRtree when installed.
- CPU/oracle is used only for correctness parity and is not reported as a performance engine.
- Each case reports cold time and repeated warm samples.
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

| Case | Rays | Triangles | Backend | Status | Median | Cold | Prepare | Blocked | Matches Oracle |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| dense_blocked:large | 8192 | 2048 | `apple_rt` | ok | 0.094030 s | 0.103164 s | n/a | 8192 | True |
| dense_blocked:large | 8192 | 2048 | `apple_rt_prepared_query` | ok | 0.057786 s | 0.073537 s | 0.043736 s | 8192 | True |
| dense_blocked:large | 8192 | 2048 | `embree` | ok | 0.003228 s | 0.025057 s | n/a | 8192 | True |
| dense_blocked:large | 8192 | 2048 | `shapely_strtree` | ok | 0.072857 s | 0.119222 s | n/a | 8192 | True |
| sparse_clear:large | 8192 | 2048 | `apple_rt` | ok | 0.055594 s | 0.052845 s | n/a | 0 | True |
| sparse_clear:large | 8192 | 2048 | `apple_rt_prepared_query` | ok | 0.033757 s | 0.042230 s | 0.018940 s | 0 | True |
| sparse_clear:large | 8192 | 2048 | `embree` | ok | 0.002870 s | 0.008210 s | n/a | 0 | True |
| sparse_clear:large | 8192 | 2048 | `shapely_strtree` | ok | 0.048831 s | 0.048775 s | n/a | 0 | True |

## Ratio Summary

- `dense_blocked:large`: Apple RT / Embree: 29.133x; Apple RT / Shapely STRtree: 1.291x; Apple RT prepared-query / Embree: 17.904x; Apple RT prepared-query / Shapely STRtree: 0.793x
- `sparse_clear:large`: Apple RT / Embree: 19.370x; Apple RT / Shapely STRtree: 1.138x; Apple RT prepared-query / Embree: 11.762x; Apple RT prepared-query / Shapely STRtree: 0.691x

## Major Conclusion

This is a useful Mac real-hardware app benchmark, but the current Apple RT path is not yet performance-leading versus Embree. All reported Apple RT, Embree, and Shapely/GEOS rows pass correctness parity on the measured scales. Embree is the fastest engine in this run. Prepared Apple RT separates obstacle setup from repeated ray queries; use that row to judge app-style repeated-query behavior.

## Interpretation Rules

- Do not treat CPU/oracle as a reported competitor in this benchmark.
- Treat Shapely absence as an environment gap, not an RTDL speed result.
- Treat Apple RT results as Mac real-hardware evidence only for the Apple RT rows that pass parity.
- Dense-blocked cases are the intended any-hit-friendly shape; sparse-clear cases expose worst-case traversal/setup behavior.
