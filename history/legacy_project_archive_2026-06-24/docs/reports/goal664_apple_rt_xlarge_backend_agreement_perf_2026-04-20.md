# Goal659: Mac Visibility/Collision Performance

Date: 2026-04-20

Status: characterization artifact

## Methodology

- Reported engines: Apple RT one-shot, Apple RT prepared-query, Embree, Shapely/GEOS STRtree when installed.
- Correctness mode: `backend_agreement`.
- Full CPU/oracle is skipped for scale; successful backends are compared by backend-output agreement.
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

| Case | Rays | Triangles | Backend | Status | Sample Median | Per-Query Median | Inner Iterations | Prepare | Blocked | Correctness Check |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| dense_blocked:xlarge_dense_backend_agreement_1s | 65536 | 16384 | `apple_rt_prepared_query` | ok | 1.049662 s | 0.052483096 s | 20 | 0.084911 s | 65536 | apple_rt_prepared_query=True |
| dense_blocked:xlarge_dense_backend_agreement_1s | 65536 | 16384 | `embree` | ok | 0.996038 s | 0.031126191 s | 32 | n/a | 65536 | apple_rt_prepared_query=True |

## Ratio Summary

- `dense_blocked:xlarge_dense_backend_agreement_1s`: Apple RT prepared-query / Embree per-query: 1.686x

## Major Conclusion

This is a useful Mac real-hardware app benchmark, but the current Apple RT path is not yet performance-leading versus Embree. Full CPU/oracle validation is intentionally skipped at this scale; successful backends are checked for canonical output agreement. Embree is the fastest engine in this run. Prepared Apple RT separates obstacle setup from repeated ray queries; use that row to judge app-style repeated-query behavior.

## Interpretation Rules

- Do not treat CPU/oracle as a reported competitor in this benchmark.
- In `backend_agreement` mode, correctness means successful backends produced the same canonical any-hit rows; it is not a full independent CPU proof.
- Treat Shapely absence as an environment gap, not an RTDL speed result.
- Treat Apple RT results as Mac real-hardware evidence only for the Apple RT rows that pass parity.
- Dense-blocked cases are the intended any-hit-friendly shape; sparse-clear cases expose worst-case traversal/setup behavior.
