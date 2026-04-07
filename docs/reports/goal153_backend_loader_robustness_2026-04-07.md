# Goal 153 Backend Loader Robustness

## Verdict

The backend loader surface is now more robust against stale shared-library
drift.

## What Changed

Loader hardening:

- [optix_runtime.py](/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py)
- [vulkan_runtime.py](/Users/rl2025/rtdl_python_only/src/rtdsl/vulkan_runtime.py)

Vulkan surface/test cleanup:

- [rtdl_vulkan.cpp](/Users/rl2025/rtdl_python_only/src/native/rtdl_vulkan.cpp)
- [rtdsl_vulkan_test.py](/Users/rl2025/rtdl_python_only/tests/rtdsl_vulkan_test.py)

New focused robustness tests:

- [goal153_backend_loader_robustness_test.py](/Users/rl2025/rtdl_python_only/tests/goal153_backend_loader_robustness_test.py)

## Main Result

If a stale Vulkan or OptiX shared library is loaded and required exports are
missing, RTDL now raises a clear diagnostic that says:

- which backend library was loaded
- which export is missing
- that the library is likely stale or built from an older RTDL checkout
- which rebuild command to use

This replaces the less helpful raw missing-symbol failure mode.

## Important Interpretation

The Antigravity report exposed a real robustness problem even though current
`main` already contains the `segment_polygon_anyhit_rows` Vulkan export in
source.

So the accepted interpretation is:

- the exact reported Linux `.so` was stale or out of sync
- but that stale-library failure path was still our product problem
- this goal fixes the user-facing robustness side of that problem

## Validation

- `python3 -m compileall src/rtdsl/vulkan_runtime.py src/rtdsl/optix_runtime.py tests/rtdsl_vulkan_test.py tests/goal153_backend_loader_robustness_test.py`
  - `OK`
- `PYTHONPATH=src:. python3 -m unittest tests.rtdsl_vulkan_test tests.goal153_backend_loader_robustness_test`
  - passing on the current local environment, with expected Vulkan availability
    skips where applicable
