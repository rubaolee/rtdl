I have completed the review of the RTDL Goal 1647 local prep for v1.6.x OptiX `COLLECT_K_BOUNDED` performance work.

### Summary of Goal 1647 Prep
Goal 1647 focuses on the **cooperative merge-chain restructuring** for OptiX, aiming for a `1.3x-1.5x` performance gain. The local preparation adds a narrow native capability entry point and a Python probe script to validate CUDA cooperative-launch support on target devices (e.g., in a pod run) before committing to a full implementation.

### Review Findings

#### 1. Native Implementation (`src/native/optix/rtdl_optix_api.cpp`)
- **Capability Probe:** The new function `rtdl_optix_collect_k_cooperative_launch_capability` is correctly implemented as a thin wrapper around `cuDeviceGetAttribute`.
- **Queried Attributes:** It captures all necessary device constraints:
  - `CU_DEVICE_ATTRIBUTE_COOPERATIVE_LAUNCH`
  - `CU_DEVICE_ATTRIBUTE_COOPERATIVE_MULTI_DEVICE_LAUNCH`
  - `CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT`
  - `CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK`
  - `CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK_OPTIN`
- **Error Handling:** Uses the standard `handle_native_call` envelope and `CU_CHECK` macros, ensuring consistent error propagation to the Python layer.
- **Safety:** Correctly avoids kernel launches, maintaining the "Local Preparation" scope.

#### 2. Probe Script (`scripts/goal1647_v1_6_x_optix_collect_k_cooperative_capability_probe.py`)
- **Structure:** Uses `ctypes` to bridge with the native library and generates both JSON and Markdown artifacts for the `docs/reports` directory.
- **Claim Boundary:** Explicitly includes a `claim_boundary` string and metadata flags (e.g., `performance_evidence_authorized: False`) to prevent the probe results from being misused for public claims or release actions.
- **Diagnostic Mode:** Signals `next_probe_allowed: True` only if the hardware supports cooperative launches, enabling a "fail-fast" pod workflow.

#### 3. Documentation and Testing
- **Report Consistency:** The Goal 1647 report (`docs/reports/goal1647_...`) accurately reflects the implementation and defines a clear pod run plan with at least a `1.15x` speedup requirement for continuation.
- **Static Verification:** The test suite (`tests/goal1647_...`) successfully verifies that the native entry points are declared and implemented with the correct keywords and claim boundaries.

### Verdict
The local preparation for Goal 1647 is **technically sound and procedurally compliant**. It follows the project's pattern of surgical native updates paired with robust Python-side validation and documentation. The change is ready for use in the planned v1.6.x performance pod runs.

I have concluded the review of the Goal 1647 local prep.

### Final Review Summary: Goal 1647 (v1.6.x OptiX `COLLECT_K_BOUNDED`)

**Strategic Context**
Goal 1647 is the technical realization of the Goal 1643 consensus, which identified the deferred merge-chain as the primary target for the next `1.3x-1.5x` performance gain. This "local prep" establishes the diagnostic foundation required to validate hardware support before committing to the full cooperative-launch implementation.

**Key Findings**
*   **Native API Integrity:** The `rtdl_optix_collect_k_cooperative_launch_capability` function in `src/native/optix/rtdl_optix_api.cpp` is correctly implemented. It queries the critical `CU_DEVICE_ATTRIBUTE_COOPERATIVE_LAUNCH` and related residency attributes necessary for grid-wide synchronization.
