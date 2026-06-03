# Goal3129: v2.8 Torch Grouped-Arg Front Door Local Smoke

Date: 2026-06-03

Status: local Linux functional smoke passed

## Purpose

Goal3126 left `grouped_argmin_f64` and `grouped_argmax_f64` as the remaining
v2.8 explicit partner-consumer front-door operations needing validation. The
local Linux Numba stack could not validate them because even a trivial Numba
CUDA kernel destroys the CUDA context on that host.

Goal3129 uses the existing local Torch CUDA target instead. This does not close
Numba-specific evidence, but it does validate the v2.8 grouped-arg front door
itself with a healthy selected partner.

## Environment

Host:

- SSH target: `192.168.1.20`
- checkout: `/home/lestat/work/rtdl_codex_local_check`
- commit: `c8d58e78`
- GPU: `NVIDIA GeForce GTX 1070`
- Torch target:
  `/home/lestat/work/rtdl_goal2685_linux_check/.pydeps_v25_triton_probe`
- Torch: `2.5.1+cu121`

This host remains functional-smoke evidence only.

## Smoke

Command shape:

```bash
cd /home/lestat/work/rtdl_codex_local_check
export PYTHONPATH=src:.:/home/lestat/work/rtdl_goal2685_linux_check/.pydeps_v25_triton_probe
timeout 240 python3 /tmp/goal3129_torch_arg_ops.py
```

Observed output:

```text
[goal3129-torch] torch 2.5.1+cu121 cuda True
[goal3129-torch] device NVIDIA GeForce GTX 1070
[goal3129-torch] case grouped_argmin_f64
[goal3129-torch] grouped_argmin_f64 groups [0, 1, 2] items [10, 20, 30] scores [1.5, 0.25, 9.0]
[goal3129-torch] claim flags False False False
[goal3129-torch] case grouped_argmax_f64
[goal3129-torch] grouped_argmax_f64 groups [0, 1, 2] items [11, 20, 30] scores [2.5, 0.25, 9.0]
[goal3129-torch] claim flags False False False
[goal3129-torch] passed grouped_argmin_f64, grouped_argmax_f64
```

Both outputs matched the Goal3114 Python reference consumer.

## Current v2.8 Partner-Front-Door Functional Coverage

Local functional smoke now covers all operations currently listed in
`V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_SUPPORTED_OPERATIONS` through at
least one healthy explicit partner:

| Operation | Local Partner Smoke | Status |
| --- | --- | --- |
| `segmented_count_i64` | CuPy | passed |
| `segmented_sum_f64` | CuPy | passed |
| `grouped_vector_sum_f64x2` | CuPy | passed |
| `grouped_argmin_f64` | Torch | passed |
| `grouped_argmax_f64` | Torch | passed |
| `grouped_topk_f64` | Torch | passed |
| `bounded_collect_finalize_i64` | Torch | passed |

Numba-specific validation for grouped argmin/argmax remains blocked on local
Linux by the independent CUDA context failure recorded in Goal3126.

## Boundaries

This does not authorize:

- a v2.8 release,
- public speedup wording,
- broad RT-core wording,
- true-zero-copy wording,
- device-residency claims,
- hidden dispatch,
- automatic partner selection,
- app-specific native-engine behavior,
- user-defined shader injection,
- benchmark-app performance claims.

## Next Step

The next step that needs pod-class hardware is not basic functional coverage of
the v2.8 partner front door; that is locally smoke-covered. The next pod-class
step is:

1. Numba-specific grouped argmin/argmax validation on a healthy CUDA stack,
2. timing/performance separation for the front-door operations,
3. larger stream sizes representative of benchmark-app continuations,
4. continued claim-boundary enforcement.
