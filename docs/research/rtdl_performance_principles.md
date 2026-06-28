# RTDL Performance Principles

RTDL is a general language and runtime for ray-tracing-shaped workloads. It is
not a hand-specialized rewrite of any single paper application.

## What RTDL Promises

1. RTDL provides generic RT primitives that can run on backends such as OptiX RT
   cores and Embree CPU BVH traversal.
2. RTDL lets users stay in Python for orchestration and app logic whenever that
   is the right productivity boundary.
3. RTDL supports app-level partners for data ingestion, layout, preprocessing,
   postprocessing, and caching.
4. RTDL should avoid unnecessary data movement, repeated materialization,
   avoidable host/device ping-pong, and avoidable Python object expansion.
5. RTDL benchmark reports must separate app ingestion, partner packing/cache,
   backend prepare, host/device transfer, native traversal, output
   materialization, and postprocess time when those phases are material.

## What RTDL Does Not Promise

1. RTDL does not promise to beat a hand-specialized C++/CUDA/OptiX
   implementation.
2. RTDL does not require benchmark apps to be rewritten as bespoke C++/CUDA
   kernels to count as successful RTDL usage.
3. RTDL does not treat avoidable Python-side ingestion or repeated packing
   overhead as an acceptable explanation for poor end-to-end performance.

## Partner Boundary

Partners are allowed and expected when the work is app-specific but not the RT
traversal primitive itself.

| Work | RTDL Engine | Partner |
| --- | --- | --- |
| Ray traversal / BVH query primitive | yes | no |
| App file format parsing | no | yes |
| App-specific packed array layout | no | yes |
| Cache or mmap of packed data | no | yes |
| Small array transforms around a primitive | no | yes |
| Replacing an RTDL primitive with an app-specific RT kernel | no for generic RTDL claims | specialized baseline only |

## Reporting Rule

When RTDL is slower than a specialized implementation, the gap must be
classified.

| Class | Meaning | Action |
| --- | --- | --- |
| Necessary generality | Cost comes from preserving generic RTDL semantics | Explain and quantify |
| Partner gap | App ingestion/layout should be handled by partner/cache | Optimize partner |
| Materialization gap | Intermediate rows or host arrays are unnecessarily materialized | Remove or fuse |
| Transfer gap | Data moves host/device more than needed | Make data resident |
| Correctness cost | Extra work enforces a stricter or different contract | State contract |
| Unknown gap | Observed speed does not match phase explanation | Not public-ready |

Short version: RTDL does what a general system should do, but it does not
promise miracles. It does promise not to waste time accidentally.
