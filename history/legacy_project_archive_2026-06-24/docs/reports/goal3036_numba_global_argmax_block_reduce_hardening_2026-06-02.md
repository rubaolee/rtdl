# Goal3036 - Numba Global Argmax Block-Reduce Hardening

Date: 2026-06-02

## Purpose

Goal3035 introduced a generic Numba partner consumer:

`global_argmax_u32_f64`

It consumes caller-supplied CUDA columns:

- `item_ids:uint32`
- `scores:float64`

and returns the row with the highest score, breaking ties by lowest item id and
then lowest row index. This is a generic continuation primitive, not an
application-specific operation.

Goal3036 hardens that consumer after the first RTX A4000 pod execution exposed
two problems in the initial implementation.

## Problems Found

1. The first implementation used global CUDA atomics over `float64` scores and
   `uint32` item ids. On the RTX A4000 pod this path destroyed the CUDA context
   during executable validation.
2. The pod dependency stack was incomplete for Numba's NVIDIA binding path.
   The legacy Numba driver path reported `cuda.is_available() == True`, but even
   a minimal `cuda.to_device(...); cuda.synchronize()` probe destroyed the
   context. Installing the newest `cuda-python` package was also wrong for this
   Numba version because it exposes the CUDA 13 `cuda.bindings` namespace while
   Numba 0.61 expects the older `cuda.cuda` module.

The working dependency boundary on this pod was:

- `numba==0.61.2`
- `numpy==2.2.6`
- `cupy-cuda12x==14.1.1`
- `cuda-python>=12,<13`
- `NUMBA_CUDA_USE_NVIDIA_BINDING=1`
- `NUMBA_CUDA_ENABLE_MINOR_VERSION_COMPATIBILITY` unset

## Change

The global argmax consumer now uses:

`multi_stage_block_reduce_no_global_atomics`

The reducer performs an initial block reduction from the input rows into block
summaries, then repeatedly reduces those summaries until one row remains. The
tie-break remains:

`highest_score_then_lowest_item_id_then_lowest_row_index`

This avoids the fragile global atomic path while keeping the same public
contract and metadata boundary.

The adapter metadata now explicitly includes:

- `operation=global_argmax_u32_f64`
- `contract=generic_global_argmax_u32_f64`
- `reduction_strategy=multi_stage_block_reduce_no_global_atomics`

## Hardware Check

The hardening was validated as a dirty overlay on the RTX A4000 pod:

- Pod: `root@157.157.221.29 -p 19771`
- GPU: NVIDIA RTX A4000, driver 580.159.03
- CUDA: `/usr/local/cuda-12.8`
- Source base commit: `3cb894783375a92bb75f8807b329792d6b6eee5d`
- Dirty overlay files:
  - `src/rtdsl/numba_partner_continuation.py`
  - `src/rtdsl/partner_adapters.py`
  - `tests/goal3035_numba_global_argmax_u32_f64_test.py`

Focused pod validation passed:

```text
Ran 5 tests in 1.136s

OK
```

This report does not claim clean-source pod validation. The next goal should
reset the pod to the committed source and record clean evidence for the composed
OptiX producer plus Numba consumer path.

## Claim Boundary

Goal3036 does not authorize:

- v2.6 release
- public speedup wording
- broad RT-core speedup wording
- true-zero-copy wording
- automatic partner selection
- app-specific native-engine behavior

This is a partner-consumer correctness and robustness hardening step. It makes
the Numba continuation executable on the RTX A4000 pod, but it is not a
same-contract performance claim.
