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
| dense_blocked:small | 512 | 128 | `apple_rt` | ok | 0.014132 s | 0.013138 s | n/a | 512 | True |
| dense_blocked:small | 512 | 128 | `apple_rt_prepared_query` | ok | 0.003323 s | 0.004134 s | 0.037824 s | 512 | True |
| dense_blocked:small | 512 | 128 | `embree` | ok | 0.000387 s | 0.024527 s | n/a | 512 | True |
| dense_blocked:small | 512 | 128 | `shapely_strtree` | ok | 0.004405 s | 0.051076 s | n/a | 512 | True |
| dense_blocked:medium | 2048 | 512 | `apple_rt` | ok | 0.021635 s | 0.029653 s | n/a | 2048 | True |
| dense_blocked:medium | 2048 | 512 | `apple_rt_prepared_query` | ok | 0.013302 s | 0.015205 s | 0.003907 s | 2048 | True |
| dense_blocked:medium | 2048 | 512 | `embree` | ok | 0.000844 s | 0.002285 s | n/a | 2048 | True |
| dense_blocked:medium | 2048 | 512 | `shapely_strtree` | ok | 0.017987 s | 0.019082 s | n/a | 2048 | True |
| sparse_clear:small | 512 | 128 | `apple_rt` | ok | 0.007903 s | 0.013247 s | n/a | 0 | True |
| sparse_clear:small | 512 | 128 | `apple_rt_prepared_query` | ok | 0.001602 s | 0.002787 s | 0.001596 s | 0 | True |
| sparse_clear:small | 512 | 128 | `embree` | ok | 0.000196 s | 0.000644 s | n/a | 0 | True |
| sparse_clear:small | 512 | 128 | `shapely_strtree` | ok | 0.004460 s | 0.003425 s | n/a | 0 | True |
| sparse_clear:medium | 2048 | 512 | `apple_rt` | ok | 0.014692 s | 0.022190 s | n/a | 0 | True |
| sparse_clear:medium | 2048 | 512 | `apple_rt_prepared_query` | ok | 0.007751 s | 0.009889 s | 0.009133 s | 0 | True |
| sparse_clear:medium | 2048 | 512 | `embree` | ok | 0.000846 s | 0.002090 s | n/a | 0 | True |
| sparse_clear:medium | 2048 | 512 | `shapely_strtree` | ok | 0.012525 s | 0.012204 s | n/a | 0 | True |

## Ratio Summary

- `dense_blocked:small`: Apple RT / Embree: 36.536x; Apple RT / Shapely STRtree: 3.208x; Apple RT prepared-query / Embree: 8.592x; Apple RT prepared-query / Shapely STRtree: 0.754x
- `dense_blocked:medium`: Apple RT / Embree: 25.624x; Apple RT / Shapely STRtree: 1.203x; Apple RT prepared-query / Embree: 15.755x; Apple RT prepared-query / Shapely STRtree: 0.740x
- `sparse_clear:small`: Apple RT / Embree: 40.269x; Apple RT / Shapely STRtree: 1.772x; Apple RT prepared-query / Embree: 8.163x; Apple RT prepared-query / Shapely STRtree: 0.359x
- `sparse_clear:medium`: Apple RT / Embree: 17.363x; Apple RT / Shapely STRtree: 1.173x; Apple RT prepared-query / Embree: 9.160x; Apple RT prepared-query / Shapely STRtree: 0.619x

## Major Conclusion

This is a useful Mac real-hardware app benchmark, but the current Apple RT path is not yet performance-leading versus Embree. All reported Apple RT, Embree, and Shapely/GEOS rows pass correctness parity on the measured scales. Embree is the fastest engine in this run. Prepared Apple RT separates obstacle setup from repeated ray queries; use that row to judge app-style repeated-query behavior.

## Interpretation Rules

- Do not treat CPU/oracle as a reported competitor in this benchmark.
- Treat Shapely absence as an environment gap, not an RTDL speed result.
- Treat Apple RT results as Mac real-hardware evidence only for the Apple RT rows that pass parity.
- Dense-blocked cases are the intended any-hit-friendly shape; sparse-clear cases expose worst-case traversal/setup behavior.
