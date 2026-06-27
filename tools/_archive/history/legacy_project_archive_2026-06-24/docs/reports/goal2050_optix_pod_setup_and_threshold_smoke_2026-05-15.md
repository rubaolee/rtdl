# Goal2050 OptiX Pod Setup and Threshold Smoke

Date: 2026-05-15

Status: `accept-with-boundary`

## Purpose

Goal2050 records the successful OptiX setup on the same NVIDIA L4 pod used for Goal2048 and confirms that the prepared OptiX fixed-radius threshold path still runs after the partner-continuation work.

This is setup and smoke evidence. It is not the exact Hausdorff witness bridge.

## Pod

- Host: `66.92.198.234`
- SSH port: `11830`
- Key used from Windows repo: `.\id_ed25519_rtdl_codex`
- GPU: NVIDIA L4
- Driver: `570.195.03`
- CUDA: `/usr/local/cuda-12`, CUDA 12.8
- OptiX SDK: `/root/vendor/optix-sdk`, tag `v8.0.0`
- Repo snapshot: local archive of commit `9b95e5f2`
- Repo path on pod: `/root/rtdl_goal2048_9b95e5f2`
- Python environment: `/root/rtdl_goal2046_venv`

## Build

Command:

```bash
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12
```

Result:

- `build/librtdl_optix.so` created.
- `ldd` resolved `libcuda.so.1`.
- `ldd` resolved `libnvrtc.so.12`.

Build log:

- `docs/reports/goal2050_build_optix.log`

## Smoke

Command shape:

```bash
PYTHONPATH=src:. \
RTDL_OPTIX_LIBRARY=/root/rtdl_goal2048_9b95e5f2/build/librtdl_optix.so \
CUDA_HOME=/usr/local/cuda-12 \
PATH=/usr/local/cuda-12/bin:$PATH \
LD_LIBRARY_PATH=/usr/local/cuda-12/targets/x86_64-linux/lib:/usr/local/cuda-12/lib64:/usr/local/cuda-12/compat:$LD_LIBRARY_PATH \
RTDL_OPTIX_PTX_ARCH=compute_89 \
RTDL_OPTIX_PTX_COMPILER=nvcc \
RTDL_NVCC=/usr/local/cuda-12/bin/nvcc \
timeout 300 /root/rtdl_goal2046_venv/bin/python \
  examples/rtdl_hausdorff_distance_app.py \
  --backend optix \
  --optix-summary-mode directed_threshold_prepared \
  --hausdorff-threshold 0.4 \
  --copies 64 \
  --require-rt-core
```

Artifact:

- `docs/reports/goal2050_optix_hausdorff_threshold_smoke.json`

Result:

- `matches_oracle`: `true`
- `oracle_decision_matches`: `true`
- `oracle_identity_matches`: `true`
- `rt_core_accelerated`: `true`
- `native_continuation_backend`: `optix_threshold_count`
- `generic_primitive`: `FIXED_RADIUS_COUNT_THRESHOLD_2D`
- `summary_primitive`: `REDUCE_INT(COUNT)`

## Boundary

Allowed claim:

- OptiX built successfully on the L4 pod.
- The prepared fixed-radius threshold decision path ran and matched the deterministic Hausdorff threshold oracle for the smoke case.

Not allowed:

- exact Hausdorff witness extraction is RT-core accelerated;
- OptiX zero-copy candidate rows feed the CuPy witness continuation;
- v2.0 release readiness;
- broad all-app speedup;
- broad RT-core speedup.

The exact witness continuation validated in Goal2048 is CuPy all-pairs partner work. The OptiX smoke here is the fast threshold decision path. Joining those into a same-contract OptiX candidate-row plus CuPy witness pipeline remains the next engineering step.

## Next Step

Goal2051 should implement or formally specify the same-contract bridge:

1. OptiX emits generic candidate/witness rows into partner-owned CuPy device columns.
2. CuPy consumes those rows with generic witness-continuation primitives.
3. The report separates traversal, candidate materialization, continuation, and total app time.
4. The result is compared against Goal2048 all-pairs CuPy and the existing threshold decision path.

## Verdict

`accept-with-boundary`
