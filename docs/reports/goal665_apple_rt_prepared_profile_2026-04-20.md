# Goal665: Apple RT Prepared Any-Hit Native Profile

Date: 2026-04-20

Status: characterization artifact

## Methodology

- Uses the native `rtdl_apple_rt_profile_prepared_ray_anyhit_2d` entry point.
- Reports native section timings inside the Apple RT prepared 2D any-hit call.
- Python wall time is included to estimate wrapper/materialization overhead outside native timing.
- This is profiling evidence, not a new performance-win claim.

## Results

### Row Materialization Path

| Case | Rays | Triangles | Prepare | Native Total | Python Wall | Buffer | Ray Pack | Dispatch/Wait | Result Scan | Output |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| dense_blocked:large | 32768 | 8192 | 0.071641 s | 0.001913 s | 0.024355 s | 0.000000 s | 0.000048 s | 0.001785 s | 0.000063 s | 0.000018 s |
| sparse_clear:large | 32768 | 8192 | 0.034387 s | 0.000866 s | 0.023812 s | 0.000000 s | 0.000051 s | 0.000644 s | 0.000060 s | 0.000016 s |

### Count-Only App Path

| Case | Rays | Triangles | Native Total | Python Wall | Buffer | Ray Pack | Dispatch/Wait | Result Scan | Output |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| dense_blocked:large | 32768 | 8192 | 0.001118 s | 0.015984 s | 0.000000 s | 0.000049 s | 0.001018 s | 0.000056 s | 0.000000 s |
| sparse_clear:large | 32768 | 8192 | 0.001164 s | 0.017393 s | 0.000000 s | 0.000047 s | 0.001061 s | 0.000054 s | 0.000000 s |

### Packed-Ray Count-Only App Path

| Case | Rays | Triangles | Native Total | Python Wall | Buffer | Ray Pack | Dispatch/Wait | Result Scan | Output |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| dense_blocked:large | 32768 | 8192 | 0.001244 s | 0.001262 s | 0.000000 s | 0.000065 s | 0.001077 s | 0.000054 s | 0.000000 s |
| sparse_clear:large | 32768 | 8192 | 0.000543 s | 0.000552 s | 0.000000 s | 0.000047 s | 0.000439 s | 0.000057 s | 0.000000 s |

## Fraction Of Native Total

- `dense_blocked:large`: buffer=0.0%, ray_pack=2.5%, dispatch_wait=93.3%, result_scan=3.3%, output=0.9%
- `sparse_clear:large`: buffer=0.0%, ray_pack=5.9%, dispatch_wait=74.3%, result_scan=6.9%, output=1.8%

## Major Conclusion

Native Apple RT traversal is not the dominant cost in the Python-facing row path. The native profiled sections are sub-millisecond to low-millisecond, while Python wall time is much larger because row dictionary materialization and repeated Python-side input packing are outside the useful RT work. The count-only path plus prepacked rays removes those two dominant costs for scalar visibility/collision apps: on the measured large cases, Python wall time falls from tens of milliseconds to sub-millisecond. The remaining boundary is output contract: this optimized path returns a scalar blocked-ray count, not the full emitted row table.
