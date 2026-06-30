# Independent Gemini Review for Goals 3967-3968: Loader Closeout and PTX Classification (2026-06-08)

**Verdict:** accept

## Review Questions and Answers:

### 1. Does Goal3967 accurately close the direct CUDA driver-module PTX loader lane without overclaiming release, speedup, true-zero-copy, AMD, package, paper reproduction, automatic partner selection, or app-specific engine claims?

**Answer:** Yes, Goal3967 accurately closes the direct CUDA driver-module PTX loader lane. The `goal3967_direct_cuda_loader_hardening_lane_closeout_2026-06-08.md` report explicitly states that the lane replaced direct CUDA driver module payloads loaded from PTX strings with CUBIN payloads. The "Boundary" section of the report clearly lists all the claims (release, speedup, true-zero-copy, AMD, package, paper reproduction, automatic partner selection, or app-specific engine claims) that are *not* authorized by this internal compatibility closeout. The associated test, `tests/goal3967_direct_cuda_loader_hardening_lane_closeout_test.py`, confirms the presence of these boundary statements in the report and verifies that the final clean packet from `goal3963` maintained its claim-boundary cleanliness.

### 2. Does the closeout correctly distinguish the tracked direct-loader debt from intentional OptiX pipeline PTX?

**Answer:** Yes, the closeout correctly distinguishes the tracked direct-loader debt from intentional OptiX pipeline PTX. The `goal3967` report explicitly notes that "OptiX pipeline PTX is intentionally still present where PTX is the OptiX program module input to pipeline construction," and that "this closeout does not try to remove or relabel it." The `goal3968` report further clarifies this distinction, stating its purpose is to ensure the project does not confuse direct CUDA driver module loads (now CUBIN-only for `cuModuleLoadData`) with OptiX program-module PTX, which intentionally feeds OptiX pipeline creation. Inspection of `src/native/optix/rtdl_optix_core.cpp` shows that the `build_pipeline` function indeed takes PTX as an input, confirming its role in OptiX pipeline construction. Furthermore, `src/native/optix/rtdl_optix_api.cpp` confirms `cuModuleLoadData` is used with `cubin.data()`.

### 3. Does Goal3968 correctly classify all remaining `compile_to_ptx(...)` workload call sites as OptiX pipeline-build inputs, and are the counts (`57` workload calls, `1` helper definition, `0` direct driver PTX payload loads) accurate?

**Answer:** Yes, Goal3968 correctly classifies all remaining `compile_to_ptx(...)` workload call sites. The `goal3968_remaining_ptx_callsite_classification_after_direct_loader_closeout_2026-06-08.md` report provides a classification table explicitly stating:
- `compile_to_ptx(...)` helper definition: 1 in `src/native/optix/rtdl_optix_core.cpp`
- workload PTX call followed by `build_pipeline(...)`: 57 in `src/native/optix/rtdl_optix_workloads.cpp`
- direct CUDA driver load using PTX payload: 0 in `src/native/**`

These counts are directly verified as accurate by `tests/goal3968_remaining_ptx_callsite_classification_after_direct_loader_closeout_test.py`. Specifically, `test_remaining_workload_ptx_call_sites_feed_optix_pipeline_builds` asserts `57` workload calls and confirms they all feed `build_pipeline`. `test_compile_to_ptx_helper_definition_count_is_stable` verifies the single helper definition, and `test_no_cuda_driver_module_load_uses_ptx_payload_anywhere_in_native_tree` confirms the absence of direct CUDA driver PTX payload loads across the `src/native` tree.

### 4. Are the Goal3967/3968 tests strong enough to guard the distinction between CUDA driver module payloads and OptiX program-module PTX?

**Answer:** Yes, the Goal3967/3968 tests are strong enough to guard this distinction.
- `tests/goal3967_direct_cuda_loader_hardening_lane_closeout_test.py` ensures the reporting and boundary claims of Goal3967 are consistent and that previous stages of the hardening lane were accepted.
- `tests/goal3968_remaining_ptx_callsite_classification_after_direct_loader_closeout_test.py` directly and comprehensively verifies the core invariants established by these goals. It rigorously checks that all identified `compile_to_ptx` calls in `rtdl_optix_workloads.cpp` are correctly paired with `build_pipeline` (confirming their role as OptiX inputs), and crucially, it performs a filesystem-wide search in `src/native` to assert that no `cuModuleLoadData` calls are using PTX payloads. This multi-faceted testing approach provides strong assurance for the maintained distinction.

### 5. What material risk remains before we leave this loader-hardening lane?

**Answer:** The primary material risk remaining is the potential for future introduction of direct CUDA driver-module PTX loader lanes or a misinterpretation of existing `compile_to_ptx(...)` calls that are not related to OptiX pipeline building. While Goal3968 has thoroughly classified existing call sites and the tests guard against current known patterns, vigilance is required to prevent the re-introduction of the "direct CUDA driver-module PTX loader lane" in new code. The current solution relies on the established invariant that `cuModuleLoadData` is used with CUBIN and `compile_to_ptx` serves OptiX pipeline construction. Any deviation from this invariant would represent a material risk.

## Details and Evidence:

- **`docs/reports/goal3967_direct_cuda_loader_hardening_lane_closeout_2026-06-08.md`**: Clearly outlines the closeout of the direct CUDA module-loader compatibility-hardening lane, specifying the replacement of PTX with CUBIN payloads and listing out-of-scope claims.
- **`tests/goal3967_direct_cuda_loader_hardening_lane_closeout_test.py`**: Validates the content and boundary claims within the Goal3967 report, and confirms the integrity of the prior `goal3963` clean packet.
- **`docs/reports/goal3968_remaining_ptx_callsite_classification_after_direct_loader_closeout_2026-06-08.md`**: Classifies `compile_to_ptx(...)` call sites, differentiating between the single helper definition, 57 workload calls feeding OptiX pipelines, and confirming 0 direct CUDA driver PTX loads. It explicitly states the useful invariants post-goal.
- **`tests/goal3968_remaining_ptx_callsite_classification_after_direct_loader_closeout_test.py`**: Provides concrete programmatic checks for the counts and classifications asserted in the Goal3968 report, including a comprehensive scan for `cuModuleLoadData` with PTX payloads across `src/native`.
- **`src/native/optix/rtdl_optix_core.cpp` and `src/native/optix/rtdl_optix_api.cpp`**: Source code confirms the existence of the `compile_to_ptx` helper and its use in `build_pipeline`, and shows `cuModuleLoadData` being used with CUBIN, supporting the distinction.
- **Prior review files (`docs/reviews/goal3956*.md`, `goal3957*.md`, `goal3960*.md`, `goal3961*.md`, `goal3964*.md`, `goal3965*.md`)**: Confirmed to exist and to have "accept" verdicts by the `goal3967` test, indicating the successful progression of the hardening lane steps.
