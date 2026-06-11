# Goal4297: Remote Pod Driver Explicit Toolchain Environment

Date: 2026-06-11

## Purpose

Convert the successful Goal4294 A40 pod recipe from a manual shell repair into
first-class remote-driver configuration.

The accepted A40 validation needed three explicit environment choices:

- Native RTDL/OptiX build CUDA prefix: `/usr/local/cuda-12.8`
- Numba CUDA/NVVM prefix: `/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc`
- External RayJoin public-CDB fixture directory outside the checkout

Before this goal, `scripts/rtdl_remote_pod_validation_driver.py` could stream
and pin refs, but it could not express those choices. A fresh driver run would
therefore drift back toward ad hoc pod repair.

## Added Driver Flags

- `--cuda-prefix`
- `--numba-cuda-prefix`
- `--rayjoin-public-cdb-dir`

The generated remote script now exports:

- `RTDL_CUDA_PREFIX` and prepends its native CUDA binaries/libraries.
- `NUMBA_CUDA_PREFIX`, `CUDA_HOME`, `CUDA_PATH`, and the Numba NVVM library
  path when a Numba prefix is supplied.
- `RTDL_RAYJOIN_PUBLIC_CDB_DIR` when an external RayJoin data directory is
  supplied.

The OptiX build command now prefers `RTDL_CUDA_PREFIX` over `CUDA_HOME`:

```bash
make build-optix OPTIX_PREFIX=... CUDA_PREFIX="${RTDL_CUDA_PREFIX:-${CUDA_HOME:-/usr/local/cuda}}"
```

That separation matters because the native library can build with CUDA 12.8
while Numba CUDA kernels use a CUDA 12.4 NVVM package to avoid unsupported-PTX
failures on a given driver.

## Boundary

This is orchestration hardening only. It does not install dependencies, choose
partners automatically, authorize release action, or change benchmark logic.

## Validation

Focused validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4297_remote_pod_driver_explicit_toolchain_env_test
```

## A40 Fresh-Clone Execution

After adding the flags, the remote driver was executed against the A40 pod with
an explicit environment:

```powershell
py -3 scripts\rtdl_remote_pod_validation_driver.py `
  --target root@194.68.245.114 `
  --port 22158 `
  --identity-file C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod `
  --build-optix `
  --optix-prefix /root/vendor/optix-dev `
  --cuda-prefix /usr/local/cuda-12.8 `
  --numba-cuda-prefix /usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc `
  --rayjoin-public-cdb-dir /root/rtdl_v2_10_validation.2dkWdf/rayjoin_public_cdb_data `
  --run-hardware `
  --run-partner-comparison `
  --timeout-scale 1.0 `
  --timeout-sec 7200 `
  --execute
```

Copied fresh-driver artifacts are stored in:

`docs/reports/goal4297_remote_driver_fresh_clone_artifacts_2026-06-11/`

Accepted facts from that packet:

- Before-build probe: `not_ready` only because `librtdl_optix.so` had not been
  built in the fresh clone yet.
- After-build probe: `ready`, with `nvcc` probing
  `/usr/local/cuda-12.8/bin/nvcc`.
- Bundle status: `pass`.
- Bundle steps: source-tree doctor, benchmark evidence index, front-door
  dry-run, scale-profile dry-run, front-door hardware, scale-profile hardware,
  and large partner comparison all passed.
- Scale-profile source commit: `e6d474e3`.
- Scale-profile working tree: clean.
- Large partner comparison: CPU-oracle matches true, one-second floor true,
  and no subsecond hot-total rows.

## Verdict

`accept`: the remote driver can now reproduce the key Goal4294 pod environment
without manual shell edits.
