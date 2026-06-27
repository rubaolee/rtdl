# Goal3126: v2.8 Torch Partner Front Door Smoke And Numba Local Boundary

Date: 2026-06-03

Status: implemented locally, Torch-smoke passed, Numba local host blocked

## Purpose

Goal3123 hardened the v2.8 explicit partner-consumer front door for the
CuPy-covered operations. Goal3126 continues the same local-only validation lane
for the remaining operations that can be tested without a pod.

## Code Hardening

File:

`src/rtdsl/v2_8_segmented_typed_stream_adapter.py`

Change:

- `bounded_collect_finalize_i64` partner execution now filters lower-level
  helper output to the canonical protocol columns:
  `{"group_ids": ..., "item_ids": ..., "row_offsets": ...}`.
- The lower-level Torch helper may still compute an auxiliary `counts` column,
  but the v2.8 bridge no longer exposes it because the canonical
  `bounded_collect_finalize_i64` operation in
  `src/rtdsl/partner_continuation_protocol.py` declares only
  `group_ids`, `item_ids`, and `row_offsets`.

Test:

`tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py`

Added a dependency-free mocked test that fails if `counts` leaks through the
v2.8 partner bridge for `bounded_collect_finalize_i64`.

## Windows Validation

```powershell
py -3 -m py_compile `
  src\rtdsl\v2_8_segmented_typed_stream_adapter.py `
  src\rtdsl\v2_8_typed_result_stream.py `
  src\rtdsl\__init__.py
```

Result: passed.

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest `
  tests.goal3111_v2_8_segmented_typed_stream_adapter_test `
  tests.goal3108_v2_8_typed_result_stream_contract_test `
  tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Observed result:

```text
Ran 27 tests in 0.014s
OK
```

## Local Linux Torch Smoke

Host:

- SSH target: `192.168.1.20`
- checkout: `/home/lestat/work/rtdl_codex_local_check`
- base commit: `e60d2fb5`
- temporary patch: Goal3126 two-file diff applied for smoke validation
- GPU: `NVIDIA GeForce GTX 1070`
- Torch target:
  `/home/lestat/work/rtdl_goal2685_linux_check/.pydeps_v25_triton_probe`
- Torch: `2.5.1+cu121`

Linux unit gate:

```text
Ran 27 tests in 0.009s
OK
```

Torch partner-consumer smoke:

```text
[goal3126-torch] torch 2.5.1+cu121 cuda True
[goal3126-torch] device NVIDIA GeForce GTX 1070
[goal3126-torch] case grouped_topk_f64
[goal3126-torch] topk groups [0, 0, 1, 1, 2] items [12, 10, 20, 21, 30] scores [0.5, 1.5, 0.25, 0.75, 9.0]
[goal3126-torch] topk claim flags False False False
[goal3126-torch] case bounded_collect_finalize_i64
[goal3126-torch] collect output keys ['group_ids', 'item_ids', 'row_offsets']
[goal3126-torch] collect groups [0, 0, 1, 2, 2] items [10, 11, 20, 30, 31] offsets [0, 2, 3, 5]
[goal3126-torch] collect claim flags False False False
[goal3126-torch] passed grouped_topk_f64, bounded_collect_finalize_i64
```

The Torch smoke confirms functional parity against the Goal3114 Python
reference consumer for:

- `grouped_topk_f64`
- `bounded_collect_finalize_i64`

## Local Linux Numba Boundary

The same local host has an isolated Numba target:

`/home/lestat/work/rtdl_goal3035_local_check/.pydeps_goal3035_numba`

Numba reports CUDA availability, but even a trivial `add_one` kernel fails at
`cuda.synchronize()` with:

```text
numba.cuda.cudadrv.driver.CudaAPIError: [709] Call to cuCtxSynchronize results in CUDA_ERROR_CONTEXT_IS_DESTROYED
```

The grouped-arg smoke failed with the same CUDA context destruction. Because a
trivial Numba kernel fails independently of RTDL, Goal3126 treats this as a
local host/Numba stack boundary, not as evidence against the v2.8 grouped-arg
front door.

## Interpretation

Goal3126 gives local functional smoke for the two Torch-covered remaining
operations and closes a bounded-collect output-schema mismatch.

It does not provide local acceptance for:

- `grouped_argmin_f64`
- `grouped_argmax_f64`

Those operations still need a pod or host with a healthy selected partner stack
for Numba/Torch/Triton as appropriate.

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

The local Linux GTX 1070 host remains functional-smoke evidence only.

## Next Step

The next meaningful validation step needs a pod or comparable CUDA host with a
healthy selected partner stack:

1. run `grouped_argmin_f64` and `grouped_argmax_f64` through the explicit v2.8
   partner-consumer front door,
2. compare against the Goal3114 Python reference consumer,
3. keep timing separate from correctness,
4. keep all claim flags blocked.
