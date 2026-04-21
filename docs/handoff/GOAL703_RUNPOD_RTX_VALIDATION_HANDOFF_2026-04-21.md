# Goal703 RunPod RTX Validation Handoff

Date: 2026-04-21

## Purpose

Use RunPod as the next practical RTX-class validation path after Google Cloud instance creation failed.

This handoff is for validating RTDL's OptiX fixed-radius and robot-collision app-performance paths on real NVIDIA RT-core hardware. It does not create cloud resources and does not contain credentials.

## Recommended Pod

Use a RunPod Pod, not Serverless.

Preferred GPU order:

1. RTX 4090
2. L40S or RTX 6000 Ada
3. L4
4. A10, A4000, or A5000

Avoid T4 unless there is no other option. T4 has first-generation RT cores and is a weak signal for current RTDL app-performance claims.

Use Secure Cloud first if availability and cost are acceptable. Community Cloud is cheaper but can add host variance; for RTDL validation, host stability matters.

## Minimal Manual Action

The user only needs to:

1. Create one RunPod GPU Pod with a CUDA development image.
2. Enable SSH or web terminal access.
3. Make the NVIDIA OptiX SDK headers available at `$HOME/vendor/optix-dev/include/optix.h`, or set `OPTIX_PREFIX` to the SDK root.
4. Run the command below.
5. Copy back the generated reports.
6. Terminate the Pod and delete any persistent storage that is no longer needed.

## Run Command Inside The Pod

```bash
curl -L https://raw.githubusercontent.com/rubaolee/rtdl/main/scripts/goal703_runpod_rtx_validation_commands.sh \
  -o /tmp/goal703_runpod_rtx_validation_commands.sh

bash /tmp/goal703_runpod_rtx_validation_commands.sh
```

If CUDA is not under `/usr/local/cuda`, set it explicitly:

```bash
CUDA_PREFIX=/usr \
NVCC=/usr/bin/nvcc \
bash /tmp/goal703_runpod_rtx_validation_commands.sh
```

The helper installs the Ubuntu packages RTDL needed on the first RunPod RTX
A5000 pod:

- `libc6-dev-i386`, needed by CUDA/NVRTC/NVCC header resolution on the tested image
- `libgeos-dev`, needed by RTDL's native oracle correctness path
- `pkg-config`, used by native dependency discovery

Set `RUNPOD_INSTALL_PACKAGES=0` if the image is prebuilt and should not run
`apt-get`.

If OptiX is extracted somewhere else:

```bash
OPTIX_PREFIX=/path/to/OptiX-SDK-root \
bash /tmp/goal703_runpod_rtx_validation_commands.sh
```

## Expected Artifacts

The script writes these files inside the RTDL checkout:

- `docs/reports/goal698_rtx_cloud_environment_YYYY-MM-DD.txt`
- `docs/reports/goal698_rtx_cloud_fixed_radius_phase_profile_YYYY-MM-DD.json`
- `docs/reports/goal703_runpod_rtx_profile_report_YYYY-MM-DD.md`

The first successful RunPod validation was on an NVIDIA RTX A5000 pod at RTDL
commit `09147a6`. The environment required OptiX headers from
`NVIDIA/optix-dev` tag `v9.0.0`, CUDA 12.4 `nvcc`, and the runtime PTX compiler
override `RTDL_OPTIX_PTX_COMPILER=nvcc`.

Copy all three files back before terminating the Pod.

## What Counts As Valid Evidence

The run is valid only if:

- `nvidia-smi` identifies an RTX-class GPU such as RTX 4090, L40S, RTX 6000 Ada, L4, or A10;
- `nvcc --version` is captured;
- OptiX headers are present and the OptiX backend builds from source;
- focused OptiX tests pass;
- the Goal697 profiler produces JSON;
- the Goal699 report generator accepts the JSON and writes the Markdown report;
- oracle parity checks pass.

## Honesty Boundaries

Do not claim broad RTDL speedup from this run.

Allowed claim if results support it:

- specific RTX-class app-level timing for fixed-radius summary modes versus row modes;
- specific RTX-class timing for robot-collision prepared scalar count versus emitted rows, if that path is run separately;
- environment-specific validation on the named RunPod GPU.

Not allowed:

- broad OptiX speedup claim for all apps;
- KNN, Hausdorff, ANN, Barnes-Hut, graph, or DB RT-core speedup claim from the fixed-radius profiler;
- AMD GPU HIPRT claim;
- Apple RT claim;
- comparison against GTX 1070 as RT-core evidence.

## Cost Control

RunPod charges running Pods for compute and storage. Stopped Pods may still retain billable storage depending on the storage type. After copying the reports, terminate the Pod and delete unused persistent/network volumes.

## If The Pod Fails

If the script stops before cloning RTDL, the likely causes are:

- the chosen template is runtime-only and does not include `nvcc`;
- the Pod lacks GPU access;
- OptiX SDK headers were not extracted.

If the script stops during `make build-optix`, keep the full terminal output. That is a real build-environment issue and should be handled as a validation blocker, not ignored.
