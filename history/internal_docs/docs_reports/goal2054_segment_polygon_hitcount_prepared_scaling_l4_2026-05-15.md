# Goal2054 Segment/Polygon Hitcount Prepared Scaling on L4

Date: 2026-05-15

Status: `accept-with-boundary`

## Purpose

Goal2054 uses the Goal2052 runner repair to gather a larger prepared-only scaling row for the segment/polygon hitcount workload on the NVIDIA L4 pod.

This goal intentionally skips the v1.8 one-shot baseline. Goal2052 already showed that the one-shot path becomes extremely expensive at 4096 rows, and for repeated-query workloads the meaningful same-contract comparison is:

- v1.8 prepared native OptiX hitcount rows;
- v2 prepared partner-owned CuPy device count columns with prepared OptiX scene and reused output columns.

## Runner Change

File:

- `scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py`

Goal2054 adds:

- `--skip-one-shot-baseline`

When enabled, the artifact keeps a `baseline` entry but marks it:

- `skipped: true`
- `query_summary: null`
- `skip_reason: explicit --skip-one-shot-baseline for large prepared-only scaling`

The v1.8 prepared baseline still runs and still checks strict parity against the expected rows.

## Pod

- Host: `66.92.198.234`
- SSH port: `11830`
- Key used from Windows repo: `.\id_ed25519_rtdl_codex`
- GPU: NVIDIA L4
- Driver: `570.195.03`
- CUDA: `/usr/local/cuda-12`, CUDA 12.8
- OptiX SDK: `/root/vendor/optix-sdk`, tag `v8.0.0`
- Repo snapshot on pod: `/root/rtdl_goal2048_9b95e5f2`
- Python environment: `/root/rtdl_goal2046_venv`
- OptiX library: `/root/rtdl_goal2048_9b95e5f2/build/librtdl_optix.so`
- Source commit label: `4e26c379-plus-goal2054-skip-one-shot`

## 8192-Row Prepared-Only Validation

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
RTDL_SOURCE_COMMIT_LABEL=4e26c379-plus-goal2054-skip-one-shot \
timeout 900 /root/rtdl_goal2046_venv/bin/python \
  scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py \
  --count 8192 \
  --iterations 3 \
  --partners cupy \
  --skip-one-shot-baseline \
  --output-capacity 262144 \
  --output /root/artifacts/goal2054_segment_polygon_hitcount_cupy_l4_8192_prepared_capacity262144.json
```

Artifact:

- `docs/reports/goal2054_segment_polygon_hitcount_cupy_l4_8192_prepared_capacity262144.json`

Result:

- status: `pass`
- count: `8192`
- output capacity: `262144`
- partner: `cupy`
- strict count parity: `true`
- expected row count: `8192`

Timing medians:

| Row | Median seconds | Ratio |
| --- | ---: | ---: |
| v1.8 one-shot native OptiX hitcount rows | skipped | skipped |
| v1.8 prepared native OptiX hitcount rows | 0.018130 | 1.000x |
| v2 unprepared partner-owned device count columns | 0.003402 | 0.188x vs v1.8 prepared |
| v2 prepared partner-owned device count columns | 0.002208 | 0.122x vs v1.8 prepared |

The prepared v2 CuPy path is about 8.2x faster than the v1.8 prepared native OptiX row path for `count=8192` with explicit witness capacity.

## 16384-Row Prepared-Only Validation

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
RTDL_SOURCE_COMMIT_LABEL=4e26c379-plus-goal2054-skip-one-shot \
timeout 900 /root/rtdl_goal2046_venv/bin/python \
  scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py \
  --count 16384 \
  --iterations 3 \
  --partners cupy \
  --skip-one-shot-baseline \
  --output-capacity 1048576 \
  --output /root/artifacts/goal2054_segment_polygon_hitcount_cupy_l4_16384_prepared_capacity1048576.json
```

Artifact:

- `docs/reports/goal2054_segment_polygon_hitcount_cupy_l4_16384_prepared_capacity1048576.json`

Result:

- status: `pass`
- count: `16384`
- output capacity: `1048576`
- partner: `cupy`
- strict count parity: `true`
- expected row count: `16384`

Timing medians:

| Row | Median seconds | Ratio |
| --- | ---: | ---: |
| v1.8 one-shot native OptiX hitcount rows | skipped | skipped |
| v1.8 prepared native OptiX hitcount rows | 0.037742 | 1.000x |
| v2 unprepared partner-owned device count columns | 0.003931 | 0.104x vs v1.8 prepared |
| v2 prepared partner-owned device count columns | 0.002313 | 0.061x vs v1.8 prepared |

The prepared v2 CuPy path is about 16.3x faster than the v1.8 prepared native OptiX row path for `count=16384` with explicit witness capacity.

## 32768-Row Prepared-Only Validation

Artifact:

- `docs/reports/goal2054_segment_polygon_hitcount_cupy_l4_32768_prepared_capacity4194304.json`

Result:

- status: `pass`
- count: `32768`
- output capacity: `4194304`
- partner: `cupy`
- strict count parity: `true`
- expected row count: `32768`

Timing medians:

| Row | Median seconds | Ratio |
| --- | ---: | ---: |
| v1.8 one-shot native OptiX hitcount rows | skipped | skipped |
| v1.8 prepared native OptiX hitcount rows | 0.102477 | 1.000x |
| v2 unprepared partner-owned device count columns | 0.004083 | 0.040x vs v1.8 prepared |
| v2 prepared partner-owned device count columns | 0.002294 | 0.022x vs v1.8 prepared |

The prepared v2 CuPy path is about 44.7x faster than the v1.8 prepared native OptiX row path for `count=32768` with explicit witness capacity.

## 65536-Row Prepared-Only Validation

Artifact:

- `docs/reports/goal2054_segment_polygon_hitcount_cupy_l4_65536_prepared_capacity16777216.json`

Result:

- status: `pass`
- count: `65536`
- output capacity: `16777216`
- partner: `cupy`
- strict count parity: `true`
- expected row count: `65536`

Timing medians:

| Row | Median seconds | Ratio |
| --- | ---: | ---: |
| v1.8 one-shot native OptiX hitcount rows | skipped | skipped |
| v1.8 prepared native OptiX hitcount rows | 0.184697 | 1.000x |
| v2 unprepared partner-owned device count columns | 0.004480 | 0.024x vs v1.8 prepared |
| v2 prepared partner-owned device count columns | 0.002351 | 0.013x vs v1.8 prepared |

The prepared v2 CuPy path is about 78.6x faster than the v1.8 prepared native OptiX row path for `count=65536` with explicit witness capacity.

## Interpretation

This is the pattern we wanted v2.0 to demonstrate for RT-heavy apps whose continuation can remain on the GPU:

1. RTDL/OptiX performs the candidate/witness traversal.
2. The output is shaped into partner-owned CuPy device columns.
3. The repeated continuation path reuses the prepared scene and output columns.
4. Python does not loop over native rows for the hot continuation.

The result is not a broad all-app speedup claim. It is a bounded, repeated-query, same-contract prepared row for one workload family. The 8192, 16384, 32768, and 65536 rows also show the useful shape of v2.0: the prepared v2 continuation is nearly flat over these sizes while v1.8 prepared row materialization grows with row count.

## Boundary

Allowed claim:

- The prepared v2 CuPy segment/polygon hitcount path scales cleanly to `count=8192` on the L4 pod with strict parity.
- The prepared v2 path is faster than the same-contract v1.8 prepared OptiX row path for this workload and artifact.
- The skip flag is appropriate for large prepared-only scaling rows where the one-shot baseline has already been measured separately.

Not allowed:

- v2.0 release readiness;
- whole-app speedup across all RTDL apps;
- broad RT-core speedup;
- package-install readiness;
- exact polygon overlay/Jaccard acceleration;
- exact Hausdorff witness bridge.

## Verdict

`accept-with-boundary`
