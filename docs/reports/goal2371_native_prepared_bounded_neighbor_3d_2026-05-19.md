# Goal2371 - Native Prepared 3D Bounded-Neighbor Search

Date: 2026-05-19

## Purpose

Goal2369 proved that packed point columns are the current large win for the
RTNN-facing 3D fixed-radius neighbor benchmark, but it also proved that the
existing `prepared-optix` path only reused Python packed inputs. It still rebuilt
and uploaded the native search-side uniform-cell structure on every timed run.

Goal2371 adds a narrow, app-agnostic native prepared handle:

- `rtdl_optix_prepare_fixed_radius_neighbors_3d`
- `rtdl_optix_run_prepared_fixed_radius_neighbors_3d`
- `rtdl_optix_destroy_prepared_fixed_radius_neighbors_3d`

The new Python facade is `prepare_optix_fixed_radius_neighbors_3d(...)`, and the
benchmark runner exposes it as `--execution-mode native-prepared-optix`.

## Design Boundary

This is a generic bounded-neighbor primitive. It is not RTNN-specific, does not
add RTNN language to the engine, and does not use RT cores. The prepared handle
builds and retains the search-side uniform-cell structure/device buffers, while
each run uploads query points, counts candidates, compacts rows, downloads rows,
and performs exact host refinement.

## Pod

- Host: `root@69.30.85.177`
- SSH port: `22055`
- GPU: NVIDIA RTX A5000
- Driver: `570.211.01`
- Checkout: `/root/work/rtdl_goal2368`
- Base commit: `963a8da4` (`Goal2369 include RTNN pod execution log`)
- OptiX SDK: `/root/vendor/optix-sdk`
- CUDA prefix: `/usr/local/cuda-12`
- Build: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12`

The reproducible packet runner is:

`scripts/goal2371_native_prepared_frn3d_pod_runner.sh`

Artifacts are in:

`docs/reports/goal2371_native_prepared_frn3d_pod/`

## Results

All native-prepared rows completed with `ok: true`. Row counts match the prior
packed `run-optix` artifacts from Goal2369.

| Points | Input | Execution | Prepare sec | Runs sec | Warm sec | Native mode | Native upload sec | Rows |
| ---: | --- | --- | ---: | --- | ---: | --- | ---: | ---: |
| 8,192 | packed-columns | run-optix | 0.000000 | 0.672458, 0.005267 | 0.005267 | uniform_cell_compact | 0.002267 | 10,322 |
| 8,192 | packed-columns | native-prepared-optix | 0.623657 | 0.000697, 0.000444 | 0.000444 | prepared_uniform_cell_compact | 0.000061 | 10,322 |
| 65,536 | packed-columns | native-prepared-optix | 0.626600 | 0.009040, 0.007685, 0.007279 | 0.007279 | prepared_uniform_cell_compact | 0.000342 | 206,434 |
| 262,144 | packed-columns | native-prepared-optix | 0.681934 | 0.104175, 0.100101, 0.090302 | 0.090302 | prepared_uniform_cell_compact | 0.003790 | 2,512,822 |

## Comparison Against Goal2369 Packed Runs

| Points | Packed run-optix warm sec | Python prepared warm sec | Native prepared warm sec | Native prepared / packed run |
| ---: | ---: | ---: | ---: | ---: |
| 65,536 | 0.010584 | 0.011261 | 0.007279 | 1.45x faster |
| 262,144 | 0.098917 | 0.101737 | 0.090302 | 1.10x faster |

## Interpretation

The new prepared handle successfully removes native search-grid rebuild/upload
from the repeated run. On the 8,192-point smoke, native upload drops from
0.002267 s to 0.000061 s and warm wall time drops from 0.005267 s to
0.000444 s.

At larger scale, the improvement is real but smaller. The 262,144-point row is
only 1.10x faster than packed `run-optix` because the remaining work is now
dominated by row download plus host exact refinement:

- native upload: 0.003790 s
- candidate count/write plus prefix/output transfer: about 0.0084 s
- exact host refine: 0.066530 s
- warm wall time: 0.090302 s

So Goal2371 closes the specific Goal2369 debt: the prepared path now reuses a
native search-side structure. The next serious RTNN performance leap is not
another Python packing fix; it is a device-resident exact/filter or row-summary
continuation so that the million-row neighbor stream does not return to the CPU
just to finish exact filtering and reduction.

## Claim Boundary

This evidence does not authorize RTNN paper equivalence, RT-core acceleration,
broad speedup, or release readiness. It is pod evidence for a generic native
prepared 3D bounded-neighbor handle under the OptiX runtime.
