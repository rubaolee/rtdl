# Goal2052 Segment/Polygon Hitcount CuPy L4 Runner Repair

Date: 2026-05-15

Status: `accept-with-boundary`

## Purpose

Goal2052 records a real pod-discovered bug in the Goal1863 segment/polygon hitcount v2 partner perf runner and the bounded L4 validation after repair.

The bug was not in the native OptiX engine or the partner output contract. The runner built OptiX ray columns (`ox`, `oy`, `dx`, `dy`, `tmax`) as float64 partner tensors, while the bounded all-witness OptiX ABI requires float32 ray columns. A large pod run therefore spent time in the v1.8 baselines and then failed before the v2 CuPy partner path could execute.

Goal2052 repairs the runner by constructing those ray columns as float32 while leaving triangle coordinate columns as float64 and triangle AABBs as float32.

It also adds an explicit `--output-capacity` override. The previous default remains `count * 2`, but larger pod runs can now size witness storage deliberately instead of failing after the expensive v1.8 baseline phase with an opaque overflow.

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
- Source commit label: `5ef65173-plus-goal2052-runner-float32`

The pod snapshot was an archive without `.git`, so the JSON artifact records `git_commit: unknown` and uses the explicit source commit label.

## Repair

File:

- `scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py`

Changed ray columns:

- `ox`: float32
- `oy`: float32
- `dx`: float32
- `dy`: float32
- `tmax`: float32

Unchanged geometry columns:

- triangle vertices: float64
- triangle AABBs: float32

This matches the OptiX ray ABI and preserves the higher-precision triangle coordinate inputs already used by the runner.

## 2048-Row L4 Validation

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
RTDL_SOURCE_COMMIT_LABEL=5ef65173-plus-goal2052-runner-float32 \
timeout 1200 /root/rtdl_goal2046_venv/bin/python \
  scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py \
  --count 2048 \
  --iterations 3 \
  --partners cupy \
  --output /root/artifacts/goal2052_segment_polygon_hitcount_cupy_l4_2048.json
```

Artifact:

- `docs/reports/goal2052_segment_polygon_hitcount_cupy_l4_2048.json`

Result:

- status: `pass`
- count: `2048`
- output capacity: `4096`
- partner: `cupy`
- strict count parity: `true`
- expected row count: `2048`

## 4096-Row Capacity Finding

An immediate 4096-row follow-up with the repaired dtype path and the default `output_capacity = count * 2` reached the v2 partner stage and failed closed:

```text
RuntimeError: partner segment/polygon column adapter overflowed; increase output_capacity
```

This is useful scaling evidence rather than a correctness failure. It shows the repaired runner enters the partner-owned device-column path at larger scale, but the default output capacity is too small for the witness multiplicity at `count=4096`. The added `--output-capacity` option makes the capacity an explicit benchmark input.

## 4096-Row L4 Validation With Explicit Capacity

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
RTDL_SOURCE_COMMIT_LABEL=5ef65173-plus-goal2052-runner-float32-capacity \
timeout 1500 /root/rtdl_goal2046_venv/bin/python \
  scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py \
  --count 4096 \
  --iterations 2 \
  --partners cupy \
  --output-capacity 32768 \
  --output /root/artifacts/goal2052_segment_polygon_hitcount_cupy_l4_4096_capacity32768.json
```

Artifact:

- `docs/reports/goal2052_segment_polygon_hitcount_cupy_l4_4096_capacity32768.json`

Result:

- status: `pass`
- count: `4096`
- output capacity: `32768`
- partner: `cupy`
- strict count parity: `true`
- expected row count: `4096`

Timing medians:

| Row | Median seconds | Ratio |
| --- | ---: | ---: |
| v1.8 one-shot native OptiX hitcount rows | 116.010651 | 1.000x |
| v1.8 prepared native OptiX hitcount rows | 0.008652 | 1.000x |
| v2 unprepared partner-owned device count columns | 0.237701 | 27.474x vs v1.8 prepared |
| v2 prepared partner-owned device count columns | 0.002321 | 0.268x vs v1.8 prepared |

The unprepared v2 median is intentionally poor at two iterations because the first sample (`0.472125` seconds) includes setup/JIT/cache cost and the second sample (`0.003277` seconds) is the steady-state query. This is why the prepared-reuse row is the meaningful same-contract row for repeated queries.

The prepared v2 CuPy path is about 3.7x faster than the v1.8 prepared native OptiX row path for `count=4096` with explicit witness capacity.

Timing medians:

| Row | Median seconds | Ratio |
| --- | ---: | ---: |
| v1.8 one-shot native OptiX hitcount rows | 14.686462 | 1.000x |
| v1.8 prepared native OptiX hitcount rows | 0.005726 | 1.000x |
| v2 unprepared partner-owned device count columns | 0.003565 | 0.623x vs v1.8 prepared |
| v2 prepared partner-owned device count columns | 0.002118 | 0.370x vs v1.8 prepared |

The prepared v2 CuPy path is about 2.7x faster than the v1.8 prepared native row path on this bounded same-contract row, and about 1.7x faster than the unprepared v2 partner path after the first-iteration setup/JIT cost.

The first unprepared v2 sample is `3.683980` seconds, while the next samples are `0.003565` and `0.002693` seconds. That first sample includes setup/JIT/cache effects and is intentionally kept in the artifact rather than hidden.

## Boundary

Allowed claim:

- The Goal1863 runner now feeds the OptiX bounded all-witness path float32 ray columns.
- A 2048-row NVIDIA L4 pod run completed with strict count parity.
- The repaired v2 CuPy prepared path is faster than the same-contract v1.8 prepared OptiX row path for this hitcount workload.
- The artifact is useful evidence for the partner-owned device-count-column contract.

Not allowed:

- v2.0 release readiness;
- whole-app speedup across all RTDL apps;
- broad RT-core speedup;
- package-install readiness;
- an exact polygon overlay/Jaccard solution;
- an exact Hausdorff witness bridge.

The JSON artifact records those boundaries with:

- `same_contract_timing_row: true`
- `partner_output_columns_true_zero_copy_authorized: true`
- `v2_0_release_authorized: false`
- `whole_app_speedup_claim_authorized: false`
- `broad_rt_core_speedup_claim_authorized: false`
- `package_install_claim_authorized: false`

## Next Step

Use this repaired runner for the broader all-app v2.0 perf table, but keep the evidence separated from release authorization until the remaining exact-continuation rows and consensus gates are satisfied.

## Verdict

`accept-with-boundary`
