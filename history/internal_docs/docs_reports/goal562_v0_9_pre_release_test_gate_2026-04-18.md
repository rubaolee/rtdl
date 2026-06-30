# Goal 562: v0.9 Pre-Release Test Gate

Date: 2026-04-18

Repository: `/Users/rl2025/rtdl_python_only`

Linux validation checkout: `/tmp/rtdl_goal562_v09_prerelease`

## Verdict

ACCEPT for the v0.9 pre-release test gate.

The local macOS-side full test discovery and Linux backend-capable full test
discovery both passed. The Linux checkout also produced explicit HIPRT
correctness and cross-backend performance/parity JSON artifacts after rebuilding
HIPRT, OptiX, Vulkan, and confirming Embree.

## Local Full Test

Command:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest discover -s tests
```

Result:

```text
Ran 232 tests in 61.191s
OK
```

Note: `python3 -m unittest discover` without `-s tests` found zero tests in
this repo layout, so it was rejected as evidence and replaced by the correct
`tests/` discovery command.

## Linux Backend-Capable Full Test

Sync command:

```bash
rsync -a --delete --exclude .git --exclude .venv --exclude build --exclude __pycache__ --exclude '*.pyc' \
  /Users/rl2025/rtdl_python_only/ \
  lestat-lx1:/tmp/rtdl_goal562_v09_prerelease/
```

Backend build commands:

```bash
cd /tmp/rtdl_goal562_v09_prerelease
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
make build-vulkan
make build-embree
```

Runtime environment:

```bash
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so
export RTDL_VULKAN_LIB=$PWD/build/librtdl_vulkan.so
export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-}
```

Full Linux test command:

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests
```

Result:

```text
Ran 232 tests in 147.650s
OK
```

## Explicit Linux HIPRT Matrix Artifacts

HIPRT correctness matrix:

- File: `/Users/rl2025/rtdl_python_only/docs/reports/goal562_hiprt_correctness_matrix_linux_2026-04-18.json`
- Summary: `pass=18`, `not_implemented=0`, `hiprt_unavailable=0`, `fail=0`

Cross-backend performance/parity matrix:

- File: `/Users/rl2025/rtdl_python_only/docs/reports/goal562_hiprt_backend_perf_compare_linux_2026-04-18.json`
- Summary: `pass=72`, `backend_unavailable=0`, `fail=0`
- Backends: `hiprt`, `embree`, `optix`, `vulkan`
- Boundary: one-repeat small-fixture smoke timing, not throughput or speedup
  evidence

## Scope Boundary

This test gate supports these statements:

- all currently discovered repo tests pass locally and on the Linux backend
  host when run with the correct `tests/` discovery root
- HIPRT is available in the Linux checkout when built against the installed
  HIPRT SDK
- HIPRT has exact row parity for the 18-workload v0.9 matrix
- HIPRT, Embree, OptiX, and Vulkan all pass the cross-backend parity smoke
  matrix

This test gate does not support these statements:

- AMD GPU validation
- RT-core speedup on GTX 1070
- HIPRT performance leadership
- production throughput benchmarking
- final `v0.9.0` release authorization by itself

## Remaining Release Work

The next gates are the v0.9 documentation audit and the whole-flow release
audit. Those should verify that all public docs, candidate release docs,
handoffs, reviews, and test artifacts line up with the current code and do not
overclaim.
