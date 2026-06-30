# Goal3007: Numba Grouped Arg Reducer Pod Runner

## Purpose

Goal3006 added the generic Numba `grouped_argmin_f64` and
`grouped_argmax_f64` preview operations. Goal3007 prepares a pod runner that
validates those operations on a modern NVIDIA GPU from a clean Git checkout.

## Runner

`scripts/goal3007_numba_grouped_arg_reducer_pod_runner.py`

The runner validates:

- an equal-score tie fixture;
- a large generic grouped score-row stream;
- direct `run_numba_grouped_argmin_f64(...)`;
- public `grouped_argmax_f64_partner_columns(..., partner="numba")`;
- CPU reference parity for compact outputs, dense outputs, missing groups, and
  present counts.

## Toolchain Boundary

The runner explicitly activates `_numba_cuda_redirector` before importing
`numba.cuda`, because `numba-cuda` installed into a `--target` dependency
directory does not have its `.pth` file processed automatically.

## Claim Boundary

This runner is conformance infrastructure only. It does not authorize:

- v2.6 release;
- public speedup wording;
- Numba speedup wording;
- RT-core speedup wording;
- whole-app speedup wording;
- true-zero-copy wording;
- automatic partner selection;
- app-specific native-engine logic.

## Expected Pod Command

```bash
PYDEPS=$PWD/.pydeps_v26_numba_cuda
export PYTHONPATH=$PYDEPS:$PWD/src:$PWD
export NUMBA_CUDA_USE_NVIDIA_BINDING=1
export NUMBA_CUDA_ENABLE_MINOR_VERSION_COMPATIBILITY=1
timeout 900 python3 scripts/goal3007_numba_grouped_arg_reducer_pod_runner.py \
  --rows 1000000 \
  --groups 4096 \
  --block-size 256 \
  --output /tmp/goal3007_numba_grouped_arg_reducer.json
```
