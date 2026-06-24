# Goal2394 RT-DBSCAN Device-Grid Baseline

Date: 2026-05-19

Status: local Linux CUDA smoke and fair-baseline implementation slice

## Why This Goal Exists

Gemini's Goal2393 review accepted Goal2392 with a boundary: it is not useful to
spend RTX pod time comparing RTDL OptiX against a weak host-side continuation.
RT-DBSCAN-style evaluation needs a fair CUDA-core baseline that keeps the grid
and component continuation on the device.

Goal2394 adds that baseline as a generic partner primitive:

```text
radius_graph_components_3d_cupy_grid_partner_columns(...)
```

This is not a DBSCAN native ABI. It is a generic 3-D radius-graph component
labeler implemented with CuPy raw kernels.

## What Changed

- Added `radius_graph_components_3d_cupy_grid_partner_columns(...)`.
- Exported it from `rtdsl.__init__`.
- Added RT-DBSCAN benchmark mode:
  `partner_cupy_grid_components_3d`.
- Updated the RT-DBSCAN README and pod runner to include the fair CUDA-core
  device-grid baseline.
- Normalized benchmark output labels so arbitrary component roots become dense
  DBSCAN labels before signature comparison.

## Local Linux Smoke Evidence

Host:

```text
lx1
NVIDIA GeForce GTX 1070, driver 580.126.09
Python 3.12.3
CuPy 14.0.1, 1 CUDA device
```

Artifacts:

- `docs/reports/goal2394_rt_dbscan_device_grid_local_linux/tiny_cupy_grid.json`
- `docs/reports/goal2394_rt_dbscan_device_grid_local_linux/clustered512_cupy_grid_validated.json`
- `docs/reports/goal2394_rt_dbscan_device_grid_local_linux/clustered4096_cupy_grid.json`
- `docs/reports/goal2394_rt_dbscan_device_grid_local_linux/clustered4096_host_bucket.json`

| Dataset | Points | Mode | Seconds | Correctness | Candidate edges | Boundary |
| --- | ---: | --- | ---: | --- | ---: | --- |
| `tiny` | 9 | CuPy device grid | 0.332333 | matches CPU reference | 12 | includes first RawKernel compile cost |
| `clustered3d` | 512 | CuPy device grid | 0.323766 | matches CPU reference | 16,081 | local CUDA smoke |
| `clustered3d` | 4096 | CuPy device grid | 0.347931 | shape recorded | 1,055,360 | no validation on large row |
| `clustered3d` | 4096 | host bucket continuation | 0.945772 | same signature | 1,055,360 | host index debt |

The local 4096 row is about 2.72x faster than the host-bucket continuation:

```text
0.945772 / 0.347931 = 2.72x
```

This is not an RTX/RT-core claim. The GTX 1070 has no RT cores. This result only
proves that the fair CUDA-core baseline is real, correct on the validated row,
and stronger than the previous host-bucket continuation.

## Current Architecture Position

RTDL now has three RT-DBSCAN-relevant layers:

1. Generic native 3-D fixed-radius traversal and prepared OptiX row output.
2. Generic partner 3-D core flags and radius-graph component labels.
3. Generic CuPy device-grid component baseline for fair CUDA comparison.

The remaining serious gap is not "write a DBSCAN kernel in the engine." The gap
is a generic bridge:

```text
OptiX fixed-radius device output -> device-resident grouped/component continuation
```

Until that bridge exists, `optix_prepared_rows` still materializes neighbor rows
and cannot fairly represent the paper's intended RT-core acceleration path.

## Next Pod Step

Use the progress-logged runner:

```text
bash scripts/goal2392_rt_dbscan_pod_runner.sh
```

The runner now includes:

- CPU correctness smoke;
- CuPy host-bucket continuation;
- CuPy device-grid continuation;
- OptiX prepared-row checks if `RTDL_OPTIX_LIBRARY` or `OPTIX_PREFIX` is
  configured.

## Verdict

Goal2394 is `accept-with-boundary`.

- Accept: a fair CUDA-core device-grid baseline exists and is locally validated.
- Boundary: no RT-core speedup, paper reproduction, or release performance claim
  is authorized from GTX 1070 local evidence.
