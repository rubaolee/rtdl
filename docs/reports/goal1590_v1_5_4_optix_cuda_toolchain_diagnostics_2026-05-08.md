# Goal 1590: OptiX CUDA Toolchain Diagnostics

## Verdict

RTDL now fails earlier and more clearly for CUDA driver/toolkit mismatches that can otherwise surface as opaque `unsupported toolchain` PTX load errors deep inside a workload.

## Changes

- Native OptiX CUDA driver errors now append an actionable hint when CUDA reports `unsupported toolchain`.
- Python OptiX runtime errors now add a matching hint before raising to users.
- The Goal1586 multi-session validation runner now performs a CUDA driver/toolkit preflight before timing.
- The preflight records `cuda_preflight` in the aggregate JSON/Markdown artifact.
- The preflight fails early when the visible `nvcc` CUDA version is newer than the CUDA version reported by `nvidia-smi` and no CUDA compat path is present in `LD_LIBRARY_PATH`.
- The preflight also fails early when a CUDA compat directory is present even though the installed driver already supports the selected toolkit version, because that can shadow the real host `libcuda` and produce `cuInit` driver-mismatch failures.
- The runner accepts `--cuda-prefix` and `--skip-cuda-toolchain-preflight`.

## User Guidance

For accepted OptiX measurements, use one of these configurations:

- A CUDA toolkit/NVRTC version supported by the installed NVIDIA driver.
- A newer CUDA toolkit with the correct driver CUDA compat library directory first in `LD_LIBRARY_PATH`.
- No CUDA compat directory when the installed driver already supports the selected toolkit; use the toolkit `lib64` path but let the process load the host driver's `libcuda`.
- A diagnostic run with `--skip-cuda-toolchain-preflight`, only when intentionally investigating an environment issue.

If PTX architecture selection is needed, set:

```bash
export RTDL_OPTIX_PTX_ARCH=compute_XX
```

where `XX` matches the target GPU architecture, for example `compute_89` for RTX 4090/Ada.

## Validation

- Local focused tests: `$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal1590_v1_5_4_optix_cuda_toolchain_diagnostics_test tests.goal1586_v1_5_4_optix_collect_k_multi_session_runner_test tests.goal1589_v1_5_4_optix_ptx_arch_override_test tests.goal1580_v1_5_4_optix_collect_k_fastest_candidate_preset_test`
- Result: `Ran 13 tests`, `OK`.

## Claim Boundary

This is configuration hardening only. It does not authorize public speedup wording, true zero-copy wording, stable primitive promotion, whole-application claims, or release action.
