# Goal1999 External Review: Goal1998 OptiX Pod Diagnosis

**Verdict:** `accept-with-boundary`

This review was performed independently by Gemini.

## Review Questions & Answers:

**1. Does the report correctly distinguish the solved SDK/header/build problem from the remaining custom-primitive OptiX module compilation blocker?**

**Yes.** The report explicitly states in its "Verdict" and "What Was Fixed" sections that the SDK installation, RTDL OptiX library build, and `libnvoptix.so.1` loading are resolved. Conversely, the "Still Blocked" section clearly identifies the persistent "Internal compiler error" when compiling custom-primitive OptiX ray/triangle any-hit modules. This distinction is clear and unambiguous.

**2. Are the source changes appropriate and bounded: compiler log capture, lazy prepared-scene pipeline compilation, float32 segment-ray columns for the candidate witness path, and the unchanged release claim boundary?**

**Yes.**
*   **Compiler log capture**: The `rtdl_optix_core.cpp` file and its corresponding test (`goal1998_optix_pod_sdk_install_and_custom_pipeline_blocker_test.py`) confirm the implementation and testing of compiler log capture during `optixModuleCreate` via `module_log` parameters.
*   **Lazy prepared-scene pipeline compilation**: The report explicitly mentions this change, and the test's `assertNotIn` for `ensure_ray_anyhit_count_2d_pipeline()` within workloads corroborates the shift from eager to lazy compilation.
*   **Float32 segment-ray columns**: The report notes that "moving the segment-ray columns for this path to float32" did not resolve the blocker, implying this change was made. The `optix_runtime.py` docstring also confirms that the C++/CUDA layer converts to float32 before uploading to the GPU.
*   **Unchanged release claim boundary**: The report's verdict, as well as `optix_runtime.py`'s internal metadata, and `scripts/goal1908_v2_local_preflight.py`'s `claim_boundary` explicitly set flags to `False` for broad claims, indicating the boundary remains unchanged.

**3. Is the `libnvoptix.so.1` / `libnvidia-gl-565` / bind-mounted-driver package caveat documented clearly enough for future pod setup?**

**Yes.** The "Reusable CUDA/OptiX Pod Setup Notes" section in the report provides detailed instructions and driver/tag guidance. It clearly explains the `libnvoptix.so.1` dependency, advises trying `libnvidia-gl-<driver>` if missing, and explicitly differentiates the `Invalid cross-device link` issue (container packaging) from SDK header problems.

**4. Do the test and preflight additions enforce the right boundary without overclaiming pod/hardware success?**

**Yes.**
*   The `goal1998_optix_pod_sdk_install_and_custom_pipeline_blocker_test.py` unit test specifically asserts the presence of both the fixed SDK issue and the *remaining* custom-primitive compilation blocker within the report, ensuring the documented status is verifiable.
*   The `scripts/goal1908_v2_local_preflight.py` script includes this test and, crucially, sets `v2_0_release_authorized`, `broad_rt_core_speedup_claim_authorized`, and `whole_app_speedup_claim_authorized` to `False` in its final output payload, indicating a conservative stance on broader claims.

**5. Are there any signs that Goal1998 accidentally authorizes v2.0 release, broad RT-core speedup, whole-app acceleration, or true pod-proven evidence?**

**No.** Both the `docs/reports/goal1998_optix_pod_sdk_install_and_custom_pipeline_blocker_2026-05-14.md` report (in its "Verdict" and "Still Blocked" sections) and the `scripts/goal1908_v2_local_preflight.py` script explicitly and repeatedly state that this work does *not* authorize v2.0 release, broad RT-core speedup, whole-app acceleration, or pod-proven RT hardware evidence for the blocked custom primitive path. The `optix_runtime.py` file's internal metadata further reinforces this by setting relevant authorization flags to `False`.

## Final Verdict

`accept-with-boundary`

Goal1998 is acceptable as a bounded diagnosis and setup-hardening goal. It does
not satisfy the final v2.0 hardware proof gate, and it should not be cited as
proof that the custom OptiX primitive path has passed pod execution.

## Independence

This review was performed by Gemini Flash as a distinct external AI system from
Codex authoring. It is useful consensus input for Goal1998, but it is not a
final v2.0 release authorization by itself.
