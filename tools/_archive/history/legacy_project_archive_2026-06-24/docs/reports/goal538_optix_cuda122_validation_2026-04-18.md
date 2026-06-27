# Goal 538: OptiX Backend Validation With CUDA 12.2.2

Date: 2026-04-18

Status: PASS after runtime PTX compatibility fix

## Scope

This goal tested whether the current RTDL OptiX backend can build and run against the new user-space CUDA 12.2.2 toolkit on the Linux validation host, without replacing system CUDA or changing the NVIDIA driver.

This is a toolchain/backend compatibility validation, not a performance claim.

## Host And Toolchain

- Linux host: `lx1`
- Kernel: `Linux lx1 6.17.0-20-generic #20~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Thu Mar 19 01:28:37 UTC 2 x86_64`
- GPU: `NVIDIA GeForce GTX 1070`
- NVIDIA driver: `580.126.09`
- Compute capability: `6.1`
- OptiX SDK include root: `/home/lestat/vendor/optix-dev/include`
- CUDA toolkit under test: `/home/lestat/vendor/cuda-12.2.2`
- CUDA compiler: `/home/lestat/vendor/cuda-12.2.2/bin/nvcc`
- CUDA compiler version: `Build cuda_12.2.r12.2/compiler.33191640_0`
- Test checkout: `/tmp/rtdl_optix_cuda122_test`
- Built library: `/tmp/rtdl_optix_cuda122_test/build/librtdl_optix.so`

## Build Command

```bash
cd /tmp/rtdl_optix_cuda122_test
rm -rf build
make build-optix \
  OPTIX_PREFIX=$HOME/vendor/optix-dev \
  CUDA_PREFIX=$HOME/vendor/cuda-12.2.2 \
  NVCC=$HOME/vendor/cuda-12.2.2/bin/nvcc
```

Build result: PASS.

## Runtime Environment

```bash
export PYTHONPATH=src:.
export RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so
export RTDL_NVCC=$HOME/vendor/cuda-12.2.2/bin/nvcc
export LD_LIBRARY_PATH=$HOME/vendor/cuda-12.2.2/lib64:${LD_LIBRARY_PATH:-}
```

The runtime probe returned:

```json
{"RTDL_NVCC": "/home/lestat/vendor/cuda-12.2.2/bin/nvcc", "RTDL_OPTIX_LIB": "/tmp/rtdl_optix_cuda122_test/build/librtdl_optix.so", "optix_version": [9, 0, 0]}
```

## Compatibility Fix

The first CUDA 12.2.2 run exposed two runtime PTX compilation issues:

1. NVRTC could not find standard host headers such as `stdint.h` for DB kernels.
2. The `nvcc` fallback needed CUDA 12.2-compatible host compiler handling on Ubuntu 24.04.

The implementation was updated in `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_core.cpp`:

- NVRTC include handling now adds existing host include fallback directories, including `/usr/include` and `/usr/include/x86_64-linux-gnu`.
- The `nvcc` fallback now uses a separate include list so it does not inherit broad host include paths that break device compilation.
- The `nvcc` fallback now passes `-allow-unsupported-compiler`.
- The `nvcc` fallback supports `RTDL_NVCC_CCBIN`; if unset and `/usr/bin/g++-12` exists, it uses that CUDA 12.2-compatible host compiler automatically.

No RTDL language-surface change was made.

## Tests Run

Command:

```bash
python3 -m unittest \
  tests.goal427_v0_7_rt_db_optix_backend_test \
  tests.goal435_v0_7_optix_native_prepared_db_dataset_test \
  tests.goal441_v0_7_optix_columnar_prepared_db_dataset_transfer_test \
  tests.goal43_optix_validation_test
```

Result:

```text
Ran 14 tests in 5.953s

OK
```

Coverage included:

- `rt.optix_version()` runtime probe
- v0.7 DB `conjunctive_scan` OptiX parity
- v0.7 DB `grouped_count` OptiX parity
- v0.7 DB `grouped_sum` OptiX parity
- native prepared OptiX DB dataset reuse
- OptiX columnar prepared DB dataset transfer
- Goal 43 OptiX validation payload coverage

## Public Examples Run

All examples passed with `--backend optix`:

- `/tmp/rtdl_optix_cuda122_test/examples/rtdl_hello_world_backends.py --backend optix`
- `/tmp/rtdl_optix_cuda122_test/examples/rtdl_db_conjunctive_scan.py --backend optix`
- `/tmp/rtdl_optix_cuda122_test/examples/rtdl_db_grouped_count.py --backend optix`
- `/tmp/rtdl_optix_cuda122_test/examples/rtdl_db_grouped_sum.py --backend optix`

Observed DB example outputs:

- `conjunctive_scan`: rows `3`, `4`
- `grouped_count`: `east=1`, `west=2`
- `grouped_sum`: `east=6`, `west=20`

## Evidence Files

- `/Users/rl2025/rtdl_python_only/docs/reports/goal538_optix_cuda122_validation_2026-04-18.log`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal538_optix_cuda122_validation_2026-04-18.json`

## Honest Boundaries

- This validates the RTDL OptiX backend with the user-space CUDA 12.2.2 toolkit on the Linux NVIDIA host.
- This does not replace the system CUDA installation.
- This does not claim a performance improvement.
- This does not validate non-NVIDIA backends.
- This does not validate RT-core acceleration because the GTX 1070 has no RT cores.

## Verdict

The RTDL OptiX backend can build and run against CUDA 12.2.2 on the Linux validation host after the runtime PTX compiler compatibility fix. Focused correctness tests and public OptiX examples pass.
