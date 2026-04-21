# Goal 696: OptiX Fixed-Radius Summary Linux Validation

**Date:** 2026-04-21
**Host:** `lestat-lx1`
**Checkout:** `/tmp/rtdl_goal696_optix_frn`
**Commit:** `c569e71 Add OptiX fixed-radius summary prototype`
**GPU:** NVIDIA GeForce GTX 1070

## Verdict

**ACCEPT for native Linux build and correctness. No performance-classification change.**

Goal695 now builds and runs on Linux with the native OptiX library. The new fixed-radius summary modes match their CPU/oracle labels and avoid materializing neighbor rows. The timing evidence is bounded whole-call evidence on a GTX 1070, which has no RT cores, so it is not RTX RT-core speedup evidence.

## Build

Command:

```bash
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
```

Result: pass.

Built library:

```text
/tmp/rtdl_goal696_optix_frn/build/librtdl_optix.so
```

Runtime probe:

```text
optix_version (9, 0, 0)
```

## Correctness

Direct helper:

```python
rtdsl.fixed_radius_count_threshold_2d_optix(...)
```

Outlier app:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
python3 examples/rtdl_outlier_detection_app.py \
  --backend optix \
  --optix-summary-mode rt_count_threshold
```

Result:

- `matches_oracle: true`
- `outlier_point_ids: [7, 8]`
- `neighbor_row_count: 0`
- `native_summary_row_count: 8`

DBSCAN app:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
python3 examples/rtdl_dbscan_clustering_app.py \
  --backend optix \
  --optix-summary-mode rt_core_flags
```

Result:

- `matches_oracle: true`
- `core_count: 7`
- `neighbor_row_count: 0`
- `cluster_rows: 0`

The `cluster_rows: 0` result is intentional in summary mode: Goal695 accelerates the DBSCAN core-flag predicate only. Full cluster expansion still belongs to the row-based app path or Python postprocess.

## Focused Tests

Command:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
python3 -m unittest -v \
  tests.goal695_optix_fixed_radius_summary_test \
  tests.goal216_fixed_radius_neighbors_optix_test \
  tests.goal690_optix_performance_classification_test
```

Result:

- 15 tests OK.
- Existing `fixed_radius_neighbors` OptiX row path still passes.
- Goal690 classification tests still pass, confirming no premature classification change.

## Timing

Timing used 3 iterations per case. These are whole-call times including Python, packing, native launch, BVH build, output copy, and app postprocess.

| Case | Points | Row Count | Summary Rows | Median s | Result |
|---|---:|---:|---:|---:|---|
| outlier rows | 128 | 320 | 0 | 0.004079 | oracle pass |
| outlier summary | 128 | 0 | 128 | 0.003654 | oracle pass |
| DBSCAN rows | 128 | 416 | n/a | 0.006348 | oracle pass |
| DBSCAN core flags | 128 | 0 | n/a | 0.005658 | oracle pass |
| outlier rows | 512 | 1280 | 0 | 0.035898 | oracle pass |
| outlier summary | 512 | 0 | 512 | 0.034565 | oracle pass |
| DBSCAN rows | 512 | 1664 | n/a | 0.068427 | oracle pass |
| DBSCAN core flags | 512 | 0 | n/a | 0.065588 | oracle pass |
| outlier rows | 1024 | 2560 | 0 | 0.131987 | oracle pass |
| outlier summary | 1024 | 0 | 1024 | 0.129375 | oracle pass |
| DBSCAN rows | 1024 | 3328 | n/a | 0.254978 | oracle pass |
| DBSCAN core flags | 1024 | 0 | n/a | 0.250226 | oracle pass |

An initial larger timing attempt including the old full-row paths at 8192 points was stopped because the row-materializing baseline became too expensive for an interactive validation run. That is consistent with the reason for the summary path, but it is not recorded as a benchmark result.

## Interpretation

The new path does what Goal695 intended:

- It builds on Linux.
- It runs through the new OptiX symbol.
- It uses native summary modes for outlier and DBSCAN core flags.
- It avoids neighbor-row materialization.
- It preserves correctness against the CPU/oracle labels.

The timing result is near parity rather than a clear speedup at these scales on GTX 1070. That is acceptable for this gate because GTX 1070 has no RT cores and this goal was correctness/build validation, not RTX performance closure.

## Boundary

No public performance-classification change should be made from this report alone.

Outlier detection and DBSCAN remain classified as `cuda_through_optix` at the app level until a future RTX-class benchmark proves that the new summary path is faster under phase-split measurement. The next required performance gate should use RTX/Ampere/Ada hardware and report build, BVH construction, launch/traversal, output copy, and Python postprocess separately.

