# Goal2375 Prepared 3D Neighbor Exact Count Summary

Date: 2026-05-19

Status: implemented and pod-validated for the count-summary contract.

## Purpose

Goal2373 showed that parallelizing the CPU exact-refine materialization loop is
not a reliable improvement. The deeper issue is that some users do not need the
full witness row stream: they need a count or downstream reduction over a
bounded-neighbor result.

Goal2375 adds a generic prepared exact-count summary path for the OptiX 3D
fixed-radius neighbor primitive. This is not an RTNN-specific engine feature.
It is a generic continuation shape:

1. Reuse the prepared native 3D uniform-cell search structure from Goal2371.
2. Upload only query points for each run.
3. Launch a device kernel that counts exact double-distance neighbors per query.
4. Download only per-query counts and return the summed count.
5. Avoid row-offset upload, row materialization, row download, and host
   exact-refine.

## New Public/Internal Surface

- Native:
  - `rtdl_optix_count_prepared_fixed_radius_neighbors_3d`
  - `fixed_radius_neighbors_3d_grid_exact_count`
- Python:
  - `PreparedOptixFixedRadiusNeighbors3D.count(...)`
  - `scripts/goal2348_rtnn_v2_2_external_runner.py --result-mode count`

The names remain app-agnostic. No native `rtnn` ABI names were added.

## Pod Environment

- Pod SSH target: `root@69.30.85.177 -p 22055`
- Repository checkout: `/root/work/rtdl_goal2368`
- Base commit: `2a2069f5` plus Goal2375 patch
- GPU: NVIDIA RTX A5000
- Driver: `570.211.01`
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12`
- Runner: `scripts/goal2375_native_prepared_frn3d_count_summary_pod_runner.sh`

## Results

| Count | Goal2371 witness rows warm sec | Goal2375 count-summary warm sec | Ratio | Goal2371 witness rows | Goal2375 exact-count summary |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 65,536 | 0.007279 | 0.006006 | 1.21x | 206,434 | 205,874 |
| 262,144 | 0.090302 | 0.003868 | 23.35x | 2,512,822 | 2,517,940 |

Phase timings:

| Count | Upload sec | Exact count kernel sec | Count download/sum sec | Row download sec | Host exact-refine sec |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 65,536 | 0.003507 | 0.000222 | 0.000152 | 0.0 | 0.0 |
| 262,144 | 0.001274 | 0.001582 | 0.000748 | 0.0 | 0.0 |

## Contract Boundary

This is a count-summary contract, not a witness-row contract.

The count summary intentionally does not claim byte-identical replacement for
Goal2371 witness rows. The witness-row path produces rows through the existing
float candidate stream plus host exact filtering and bounded materialization.
The new count-summary path counts exact double-distance neighbors directly on
the device and returns only the aggregate count. Near radius boundaries and
queries with more than `k_max` valid neighbors can therefore differ from the
materialized witness-row count.

This is a useful result, not a broad claim:

- It does not authorize an RT-core speedup claim.
- It does not claim RTNN paper equivalence.
- It does not replace witness rows when users need neighbor IDs or distances.
- It is valid evidence that RTDL can expose a faster generic continuation when
  the user asks for a summary rather than a row stream.

## Design Lesson

The v2.2 nearest-neighbor campaign should not try to make every app faster by
materializing every candidate row. RTDL needs first-class generic continuation
contracts:

- witness rows when users need IDs/distances;
- exact count summaries when users need counts;
- future device-resident reductions when users need min/max/sum over the
  neighbor stream.

That keeps the engine app-agnostic while still letting serious applications use
the fastest contract that matches their actual output requirement.
