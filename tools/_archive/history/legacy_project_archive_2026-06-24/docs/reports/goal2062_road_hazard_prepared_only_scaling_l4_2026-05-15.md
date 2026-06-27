# Goal2062 Road Hazard Prepared-Only Scaling on L4

Date: 2026-05-15

Status: `accept-with-boundary`

## Purpose

Goal2062 resolves the road-hazard runner debt identified in Goal2060. The previous `count=8192` road-hazard attempt spent pod time in the v1.8 one-shot baseline with `output_capacity=100663296`, which was not the useful repeated-query comparison.

Goal2062 adds a `--skip-one-shot-baseline` option to:

- keep the one-shot baseline explicitly marked as skipped;
- preserve the v1.8 prepared baseline;
- preserve v2 unprepared and v2 prepared partner timing rows;
- allow large same-contract prepared scaling without hiding what was omitted.

## Runner Change

File:

- `scripts/goal1869_road_hazard_v2_partner_perf.py`

Added:

- `--skip-one-shot-baseline`
- nullable `query_median_ratio_vs_v1_8_one_shot_native` when the one-shot baseline is skipped
- `baseline.skipped: true`
- `baseline.skip_reason: explicit --skip-one-shot-baseline for large prepared-only scaling`

## Pod Result

Artifact:

- `docs/reports/goal2062_road_hazard_cupy_l4_8192_prepared_only.json`

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
RTDL_SOURCE_COMMIT_LABEL=05fbfccb-plus-goal2062-road-skip-one-shot \
timeout 1200 /root/rtdl_goal2046_venv/bin/python \
  scripts/goal1869_road_hazard_v2_partner_perf.py \
  --count 8192 \
  --iterations 3 \
  --partners cupy \
  --skip-one-shot-baseline \
  --output /root/artifacts/goal2062_road_hazard_cupy_l4_8192_prepared_only.json
```

Result:

- status: `pass`
- count: `8192`
- hazards: `12288`
- output capacity: `100663296`
- strict priority flag parity: `true`
- prepared scene reused: `true`
- witness output columns reused: `true`
- whole-app true-zero-copy metadata: `true`

Timing medians:

| Row | Median seconds | Ratio |
| --- | ---: | ---: |
| v1.8 one-shot native OptiX rows | skipped | skipped |
| v1.8 prepared native OptiX rows | 0.021176 | 1.000x |
| v2 unprepared partner priority flags | 0.007782 | 0.367x vs prepared |
| v2 prepared partner priority flags | 0.002384 | 0.113x vs prepared |

The prepared v2 CuPy road-hazard path is about 8.9x faster than the same-contract v1.8 prepared OptiX row path for `count=8192`.

## Interpretation

This materially improves the Goal2060 road-hazard finding. At `count=1024`, v2 prepared was slightly slower than v1.8 prepared. At `count=8192`, after avoiding the irrelevant one-shot baseline, v2 prepared is clearly faster.

The useful pattern matches Goal2054:

1. v1.8 prepared still materializes row-shaped output.
2. v2 keeps the exact filter and count materialization on partner GPU columns.
3. Prepared scene and output columns are reused.
4. The partner continuation amortizes its overhead at larger scale.

## Boundary

Allowed claim:

- The road-hazard v2 prepared partner path is faster than the v1.8 prepared native OptiX row path at `count=8192` on the L4 pod.
- The runner now supports honest prepared-only large scaling by marking the one-shot baseline as skipped.

Not allowed:

- v2.0 release readiness;
- broad all-app speedup;
- broad RT-core speedup;
- package-install readiness;
- one-shot speedup for the skipped 8192 baseline.

## Verdict

`accept-with-boundary`
