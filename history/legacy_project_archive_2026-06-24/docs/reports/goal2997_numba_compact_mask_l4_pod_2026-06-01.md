# Goal2997: Numba Compact Mask L4 Pod Evidence

Date: 2026-06-01

Status: passed on NVIDIA L4 pod.

## What This Proves

Goal2997 adds runtime conformance evidence for `compact_mask_i64` on the v2.6
user-selected Numba lane.

The primitive turns a device-resident boolean mask into stable selected row
indices and selected values. This is useful for RayJoin-style and
triangle-counting-style continuations, but the primitive itself is generic and
app-agnostic.

## Pod Environment

- SSH endpoint supplied by the user: `root@157.157.221.29 -p 29842`
- Key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- GPU: `NVIDIA L4`
- Driver: `565.57.01`
- Source commit: `afca574838d2519def88c9bed45d999a4e0b153b`
- Numba version: `0.65.1`
- NumPy version: `2.1.2`
- Isolated Numba CUDA module:
  `/root/rtdl_goal2991_v26_pod/.pydeps_v26_numba_cuda/numba_cuda/numba/cuda/__init__.py`
- Required environment:
  `NUMBA_CUDA_USE_NVIDIA_BINDING=1`
  `NUMBA_CUDA_ENABLE_MINOR_VERSION_COMPATIBILITY=1`

## Run

Runner:

`scripts/goal2997_numba_compact_mask_pod_runner.py`

Parameters:

- rows: `1,000,000`
- block size: `256`

Artifact:

`docs/reports/goal2997_numba_compact_mask_l4_pod_2026-06-01.json`

## Results

- selected count: `193,279`
- operation: `compact_mask_i64`
- values match CPU: true
- original indices match CPU: true
- `partner_mask_indices(..., partner="numba")` indices match CPU: true
- stable input order: true
- host prefix sum used: true

## Boundary

This is runtime conformance evidence for one generic Numba continuation
primitive. It does not authorize:

- v2.6 release
- public speedup claims
- whole-app speedup claims
- broad RT-core speedup claims
- true zero-copy claims
- Numba speedup claims
- automatic partner selection claims

The current implementation is correctness-first: it preserves stable order using
per-block counts and a host prefix sum. A future performance pass may replace
that host prefix sum with a device-resident scan, but that is not claimed here.
