# Goal3842 RayJoin PIP Batch Executor Current Refresh

Date: 2026-06-08

Status: internal performance evidence; no release or public speedup
authorization.

## Purpose

Goals3833/3834 showed that the bounded 512 public-CDB PIP scalar-count row is
still faster with app-side CUDA-core partner code than with the one-shot
RTDL/OptiX route. Goal3841 then tightened the advisory wording so readers do
not overread the separate Goal3761 native-PIP cross-size packet.

Goal3842 refreshes the useful RTDL/OptiX PIP contract on current `main`: a
resident prepared point/closed-shape batch-count executor. This is the generic
way to make small PIP requests fast when the app can issue repeated requests
over prepared inputs.

## Pod Evidence

Pod:

`ssh root@69.30.85.203 -p 22057 -i ~/.ssh/id_ed25519`

Repository commit:

`09a31f30717ce53624df6bc4b73b1b80a81d4eb7`

GPU:

`NVIDIA RTX A5000, 580.126.09`

Artifact:

`docs/reports/goal3842_rayjoin_pip_batch_executor_current_a5000/summary.json`

Command shape:

```bash
PYTHONPATH=.pydeps_goal3788_numba:src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS=1e-9 \
python3 scripts/goal3310_rayjoin_pip_batch_scalar_count_probe.py \
  --dataset /root/rtdl_goal3293/data/rayjoin_public_cdb/br_county_start256_count512.cdb \
  --output docs/reports/goal3842_rayjoin_pip_batch_executor_current_a5000/summary.json \
  --scalar-count-pipeline \
  --batch-executor \
  --batch-stream-count auto \
  --single-warmup 5 \
  --single-repeat 50 \
  --batch-warmup 5 \
  --batch-repeat 30 \
  --request-counts 1 4 8 16 32 64 100
```

The `RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS=1e-9` setting is required
for this public-CDB slice. Without it, the device-filtered inclusive path
overcounts boundary-adjacent points (`1429` instead of `1417`).

## Results

All measured rows returned exact count `1417`.

| Request count | Effective streams | Median ms/request | Median total ms |
| ---: | ---: | ---: | ---: |
| 1 | 1 | 0.218613 | 0.218613 |
| 4 | 1 | 0.200112 | 0.800447 |
| 8 | 4 | 0.056849 | 0.454793 |
| 16 | 8 | 0.032043 | 0.512689 |
| 32 | 8 | 0.028729 | 0.919314 |
| 64 | 16 | 0.026915 | 1.722566 |
| 100 | 16 | 0.024183 | 2.418306 |

Compared with the one-request executor row, the 100-request batch row is about
`9.04x` faster per request.

## Graph Replay Check

A live current-main smoke confirmed the older Goal3312 negative result remains
true:

- scalar-count pipeline graph replay: `(0, 0, 0)` instead of `(1417, 1417,
  1417)`;
- row pipeline graph replay: `(0, 0, 0)` instead of `(1417, 1417, 1417)`.

The Python graph wrapper remains fail-closed when validation is enabled. This
packet does not use graph replay as performance evidence.

## Interpretation

The PIP story now has three explicit lanes:

- One-shot bounded 512 public-CDB PIP remains CuPy-favorable, with a Numba
  no-RawKernel reference from Goal3834.
- Resident repeated-request PIP is RTDL/OptiX-favorable through the generic
  prepared point/closed-shape batch executor.
- CUDA graph replay for this prepared PIP batch remains blocked by a zero-count
  replay failure.

This is a runtime-contract improvement, not a RayJoin paper reproduction or a
universal PIP-dominance claim.

## Claim Boundary

Goal3842 does not authorize:

- release action;
- public speedup wording;
- whole-app RayJoin wording;
- RayJoin paper reproduction claims;
- RTDL-beats-RayJoin claims;
- broad RT-core speedup claims;
- true zero-copy claims;
- automatic partner/backend selection.
