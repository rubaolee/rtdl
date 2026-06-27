# Vulkan and HIP RT Engine Status Report

**Date**: 2026-04-23
**Environment**: Cloud RTX 4090 Node (Linux-6.8.0-85-generic-x86_64)

## Objective
This report assesses the current build and runtime status of the Vulkan and AMD HIP RT backends within the active cloud test environment, based on the findings from the `goal778_rtx4090_extra_gpu_backend_batch` probe.

## 1. Vulkan Engine Status
**Status: Unavailable / Broken**

The Vulkan backend is currently non-functional in the active environment due to both build-time and run-time failures.

*   **Build Failure**: Running `make build-vulkan` fails because the `shaderc` compiler dependency is missing from the host system.
    ```text
    fatal error: shaderc/shaderc.h: No such file or directory
    ```
*   **Runtime Failure**: Even if the library were built, the host environment has an incompatible or misconfigured Vulkan driver installation. `vulkaninfo` fails during instance creation:
    ```text
    Could not get 'vkCreateInstance' via 'vk_icdGetInstanceProcAddr' for ICD libGLX_nvidia.so.0
    Cannot create Vulkan instance.
    ```
*   **Impact**: All Vulkan unit tests (34 tests) gracefully detect the missing backend and skip execution rather than crashing. The Vulkan engine provides no performance or correctness coverage on this node.

## 2. AMD HIP RT Engine Status
**Status: Unavailable / Missing SDK**

The HIP RT backend cannot be built or tested on the current NVIDIA-provisioned node.

*   **Build Failure**: Running `make build-hiprt` immediately fails because the AMD HIP RT SDK is not present at the expected vendor path.
    ```text
    HIPRT SDK header not found at /root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/hiprt.h
    ```
*   **Runtime Impact**: Because the library (`librtdl_hiprt.so`) cannot be built, the Python loader safely catches the missing library. All 59 HIP RT tests skip execution with the message `'HIPRT runtime is not available'`.
*   **Context**: Given that this is an NVIDIA RTX 4090 node, the absence of the AMD HIP RT SDK is expected, but it confirms that cross-vendor comparative benchmarking cannot be performed in this specific session.

## Summary Conclusion
Both the Vulkan and HIP RT engines are unavailable in the current RTX 4090 cloud environment due to missing SDKs (`shaderc`, `hiprt.h`) and incompatible driver layers (Vulkan ICD). The Python test harness correctly handles these absences by gracefully skipping the relevant tests. All current performance and correctness validation on this node must rely exclusively on the `cpu`, `embree`, and natively supported `optix` backends.
