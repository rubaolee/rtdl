# Goal4437 / V3.0 M40 - Numba CUDA Toolchain Autoconfig

## Result

M40 adds `configure_numba_cuda_toolchain_environment()` and calls it before
importing `numba.cuda` through RTDL's Numba partner bootstrap.

The helper auto-detects the pip CUDA compiler package at:

```text
nvidia/cuda_nvcc
```

When found, it makes that package visible to Numba by setting or prepending:

- `NUMBA_CUDA_PREFIX`
- `CUDA_HOME`
- `CUDA_PATH`
- `PATH`
- `LD_LIBRARY_PATH`
- `NUMBA_CUDA_DRIVER`

The helper is useful for launchers and child processes, and it gives RTDL a
single place to report the intended Numba CUDA toolchain. It does not install
packages and it does not replace the pod setup runbook.

## Why

M39 reproduced the known Numba partner failure on the RTX 4000 Ada pod:

```text
PTX 8.7 versus PTX 8.4
```

The project already had a runbook fix in
`scripts/goal3975_current_scale_partner_pod_setup.sh`. M40 moves the environment
discovery into RTDL's Numba bootstrap so launchers and subprocesses can reuse
the same CUDA 12.4 compiler-package paths without duplicating the discovery
logic.

The measured pod runs still need the runbook exports before Python starts.
That ordering matters on this driver-550 pod: setting `LD_LIBRARY_PATH` and
`NUMBA_CUDA_DRIVER` inside an already-running Python process is too late for
Numba 0.60's driver/toolchain availability probe.

## Boundary

This helper:

- does not install packages
- does not configure RTDL native OptiX
- does not change OptiX build inputs
- does not authorize public speedup claims
- does not make Numba an automatic hidden partner choice

It only prepares the process environment for explicit Numba partner execution.
The bootstrap must run before a caller imports `numba.cuda` directly; RTDL's own
Numba partner entrypoints satisfy that ordering.
For live CUDA execution on this pod, live Numba partner runs still need
process-level exports from the runbook before Python starts.

- live Numba partner runs still need process-level exports

## Pod Check

After the runbook exports, M39 passes on the repaired pod:

```text
export NUMBA_CUDA_PREFIX=/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc
export CUDA_HOME=$NUMBA_CUDA_PREFIX
export PATH=$NUMBA_CUDA_PREFIX/bin:/usr/local/cuda-12/bin:$PATH
export LD_LIBRARY_PATH=$NUMBA_CUDA_PREFIX/nvvm/lib64:/usr/local/cuda-12/targets/x86_64-linux/lib:/usr/local/cuda-12/lib64:${LD_LIBRARY_PATH:-}
export NUMBA_CUDA_DRIVER=/lib/x86_64-linux-gnu/libcuda.so.1
PYTHONPATH=src:. python3 -m unittest tests.goal4436_v3_0_m39_prepared_aggregate_frontier_numba_pipeline_test -v
```

The no-export in-process probe no longer crashes, but it skips live CUDA on this
pod because Numba sees CUDA availability before runtime `LD_LIBRARY_PATH`
changes can help. That is a process-start constraint, not an RTDL primitive
contract issue.
