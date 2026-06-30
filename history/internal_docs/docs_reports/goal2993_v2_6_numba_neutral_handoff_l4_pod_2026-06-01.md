# Goal2993 - v2.6 Numba Neutral Handoff L4 Pod Evidence

Date: 2026-06-01

## Purpose

Goal2993 records the first accepted CUDA pod execution of the v2.6 neutral
partner handoff from Goal2990 using the Goal2991 Numba continuation runner.
The purpose is to prove that a user-selected Numba partner can consume
device-resident columns through the neutral handoff without the legacy torch carrier or torch conversion path.

## Pod

- Host: `d82fc5502d11`
- GPU: `NVIDIA L4`
- Driver: `565.57.01`
- Driver CUDA capability reported by `nvidia-smi`: `12.7`
- Python: `3.12.3`
- Source commit: `ed36a366cca2ddbaf2f33bcb89393de9f24bf3d5`
- Artifact:
  `docs/reports/goal2993_v2_6_numba_neutral_handoff_l4_pod_2026-06-01.json`

## Toolchain Resolution

The first pod attempt exposed a real toolchain issue: the default pip Numba
CUDA target emitted PTX `.version 8.7`, while the pod driver linker accepted
PTX `8.6`. Pinning older built-in Numba did not fix it because the built-in
CUDA target still emitted the same PTX version on this Python 3.12 stack.

The working configuration uses NVIDIA's out-of-tree CUDA target for Numba:

- `numba-cuda[cu12]` installed in an isolated local target directory.
- The target directory is activated as a site directory so its `.pth`
  redirector can route `numba.cuda` to `numba_cuda/numba/cuda`.
- `NUMBA_CUDA_USE_NVIDIA_BINDING=1`
- `NUMBA_CUDA_ENABLE_MINOR_VERSION_COMPATIBILITY=1`

The resulting artifact records:

- `numba_version`: `0.65.1`
- `numpy_version`: `2.1.2`
- `numba_cuda_module`:
  `.pydeps_v26_numba_cuda/numba_cuda/numba/cuda/__init__.py`
- `numba_cuda_use_nvidia_binding`: `1`
- `numba_cuda_enable_minor_version_compatibility`: `1`

This is an environment/toolchain fix, not an RTDL algorithm change.

## Result

The large run passed:

- Rows: `1,000,000`
- Groups: `4,096`
- Block size: `256`
- Selected partner: `numba`
- Neutral handoff validation: `accept`
- Runtime-observed descriptor count: `2`
- All columns device resident: `true`
- All leases completed: `true`
- Torch conversion used: `false`
- Torch carrier used: `false`
- Segmented count CPU parity: `true`
- Segmented sum CPU parity: `true`
- Maximum sum absolute error: `9.094947017729282e-13`

The recorded partner-continuation timings were:

- Count: `0.038955722004175186s`
- Sum: `0.04132115840911865s`
- Total runner elapsed time: `1.222635943442583s`

These timings are retained as diagnostics for the Numba continuation path. They
do not authorize public speedup wording because no same-contract baseline
comparison was part of Goal2993.

## Boundary

Goal2993 upgrades the v2.6 N-0/N-1 state from "runner prepared" to "large L4 pod runtime conformance passed" for Numba segmented count/sum through the
neutral partner handoff.

It does not authorize v2.6 release, public speedup wording, whole-app speedup
wording, broad RT-core wording, true-zero-copy wording, Numba speedup wording,
automatic partner selection, automatic Triton selection, or app-specific native
engine behavior.

## Next

The next v2.6 work should move from generic Numba continuation conformance to a
benchmark-app demonstration:

1. Choose one benchmark app whose continuation naturally maps to segmented
   count/sum or a small extension of that family.
2. Route that app through explicit user-selected `partner="numba"`.
3. Keep a partner-free reference path and CPU parity.
4. Add same-contract timing only after correctness is locked.
