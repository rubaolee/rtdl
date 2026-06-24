# Goal 764: RTX Cloud OptiX Bootstrap Blocker

Date: 2026-04-22

## Verdict

`BLOCKED_FOR_NATIVE_OPTIX_BENCHMARKS`

The RunPod RTX A5000 host is reachable and has CUDA/NVIDIA runtime support, but it cannot currently run RTDL native OptiX workloads because the available unattended OptiX SDK header source is OptiX 9.1 while the host driver is R580. OptiX 9.1 requires an R590+ driver according to NVIDIA's public download page. The compatible target for this host is OptiX SDK 9.0.0 or 8.1.0, but NVIDIA gates official SDK downloads behind Developer Program login.

This is an environment/bootstrap blocker, not evidence that RTDL apps are slow or incorrect on RTX hardware.

## Cloud Host Evidence

- SSH target: `n8tpfheut85rz1-64411542@ssh.runpod.io`
- SSH key used: `/Users/rl2025/.ssh/id_ed25519_rtdl_codex`
- Remote repo path: `/workspace/rtdl_python_only`
- Remote branch: `codex/rtx-cloud-run-2026-04-22`
- Remote commit: `db8a062400e649593a5092d0b3ffec43bb4515aa`
- GPU: `NVIDIA RTX A5000`
- Driver: `580.126.09`
- GPU memory: `24564 MiB`
- CUDA toolkit: `/usr/local/cuda`
- NVCC: `/usr/local/cuda/bin/nvcc`
- NVCC version: `Cuda compilation tools, release 12.4, V12.4.131`

## What Passed

- The pod is reachable with the selected key.
- The project branch was fetched and checked out on the pod.
- CUDA headers and `nvcc` are present.
- `nvidia-smi` sees the RTX A5000.
- `make build-optix` can compile `build/librtdl_optix.so` when pointed at an OptiX include tree.
- The portable parts of the focused OptiX tests still run.

## What Failed

The first bootstrap run used `/root/vendor/optix-dev`, cloned from NVIDIA's public `optix-dev` mirror. That mirror currently provides OptiX 9.1 headers:

- `OPTIX_VERSION 90100`
- `OPTIX_ABI_VERSION 118`

The native RTDL OptiX tests then failed with:

```text
RuntimeError: OptiX error: Unsupported ABI version
```

This is consistent with NVIDIA's public compatibility note that OptiX 9.1 requires an R590 or newer driver, while the pod has R580.

## Workarounds Tried

- Tried building against the public OptiX 9.1 header mirror. Build succeeded, runtime failed with unsupported ABI.
- Tried patching the public header ABI value downward. This is not a valid release solution and produced unstable behavior, including SSH session resets when native OptiX entry points were executed.
- Tried direct unauthenticated access to the OptiX 9.0.0 Linux SDK URL. The request redirected to NVIDIA login, so the official SDK cannot be fetched unattended from this environment.
- Confirmed `RTDL_NVCC=/usr/local/cuda/bin/nvcc` is also needed on this pod when forcing `RTDL_OPTIX_PTX_COMPILER=nvcc`; otherwise the runtime looks for `/usr/bin/nvcc`.

## Required Resolution

One of these must happen before valid RTX A5000 native OptiX app benchmarks can be run:

1. Use a RunPod image/host with NVIDIA R590+ driver, then use the public OptiX 9.1 header mirror.
2. Manually download OptiX SDK 9.0.0 or 8.1.0 from NVIDIA Developer Program and place the extracted SDK on the pod.
3. Use a different cloud image that already includes a driver-compatible OptiX SDK header bundle.

After that, rerun:

```bash
cd /workspace/rtdl_python_only
export OPTIX_PREFIX=/path/to/compatible/optix-sdk
export CUDA_PREFIX=/usr/local/cuda
export NVCC=/usr/local/cuda/bin/nvcc
export RTDL_NVCC=/usr/local/cuda/bin/nvcc
export RTDL_OPTIX_PTX_COMPILER=nvcc
export RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so

PYTHONPATH=src:. python3 scripts/goal763_rtx_cloud_bootstrap_check.py \
  --output-json docs/reports/goal763_rtx_cloud_bootstrap_check_runpod_2026-04-22.json

PYTHONPATH=src:. python3 scripts/goal761_rtx_cloud_run_all.py \
  --output-json docs/reports/goal761_rtx_cloud_run_all_summary_runpod_2026-04-22.json

PYTHONPATH=src:. python3 scripts/goal762_rtx_cloud_artifact_report.py \
  --summary-json docs/reports/goal761_rtx_cloud_run_all_summary_runpod_2026-04-22.json \
  --output-json docs/reports/goal762_rtx_cloud_artifact_report_runpod_2026-04-22.json \
  --output-md docs/reports/goal762_rtx_cloud_artifact_report_runpod_2026-04-22.md
```

## Honesty Boundary

No RTX app performance result was produced in this attempt. Any public RT-core acceleration claim remains unauthorized until a compatible OptiX SDK/driver pair passes Goal763 and the Goal761/Goal762 benchmark pipeline completes.
