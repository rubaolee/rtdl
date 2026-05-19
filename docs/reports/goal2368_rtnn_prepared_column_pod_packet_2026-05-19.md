# Goal2368 - RTNN Prepared Column Pod Packet

Date: 2026-05-19

## Purpose

Goal2368 prepares the next GPU-pod run for the v2.2 RTNN campaign. Goal2363
showed that packed columns remove Python record-normalization overhead.
Goal2365 added `prepared-optix` execution mode. This packet makes the next pod
run repeatable instead of manual.

## Runner

`scripts/goal2368_rtnn_prepared_column_pod_runner.sh`

The runner:

1. Records repo head, GPU/driver, CUDA paths, and OptiX prefix.
2. Builds `build/librtdl_optix.so`.
3. Generates deterministic synthetic 3D point clouds at 65,536 and 262,144
   points.
4. Runs three RTDL modes at each scale:
   - `records` + `run-optix`
   - `packed-columns` + `run-optix`
   - `packed-columns` + `prepared-optix`
5. Emits JSON artifacts under
   `docs/reports/goal2368_rtnn_prepared_column_pod/`.

Each step is wrapped by `timeout` and prints `START` / `DONE` progress lines so
pod sessions do not silently hang.

## Default Command

```bash
cd /root/work/rtdl
RTDL_ROOT=/root/work/rtdl \
OPTIX_PREFIX=/root/vendor/optix-sdk \
STEP_TIMEOUT_SECONDS=900 \
bash scripts/goal2368_rtnn_prepared_column_pod_runner.sh
```

If the pod uses CUDA 12 beside a CUDA 13 default, pass:

```bash
CUDA_PREFIX=/usr/local/cuda-12
```

## Claim Boundary

This packet does not authorize RTNN paper equivalence, RT-core acceleration, a
public speedup claim, or release readiness. It is a controlled v2.2 measurement
packet for the current generic uniform-cell bounded-neighbor path and the new
packed/prepared Python API shape.

## Expected Use

When a pod is available, run this packet first. It should tell us whether the
large-scale delta is now dominated by native execution, input packing,
prepared-binding overhead, or output materialization.
