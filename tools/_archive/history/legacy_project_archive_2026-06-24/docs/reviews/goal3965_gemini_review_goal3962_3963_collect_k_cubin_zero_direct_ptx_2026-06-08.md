# Independent Gemini Review for Goals3962-3963 Collect-K CUBIN / Zero Direct PTX

Date: 2026-06-08

## Verdict

**accept**

## Review Answers

1.  **Does Goal3962 correctly convert the remaining collect-k direct CUDA helper module loaders to `compile_to_cubin(...)` plus `cuModuleLoadData(..., cubin.data())`?**
    Yes. The `docs/reports/goal3962_collect_k_direct_cuda_cubin_loader_hardening_2026-06-08.md` explicitly states this conversion. Furthermore, `tests/goal3962_collect_k_direct_cuda_cubin_loader_hardening_test.py` contains `test_collect_k_direct_cuda_loaders_use_cubin` which verifies the presence of `compile_to_cubin` and `cuModuleLoadData(..., cubin.data())` for the specified kernels, and `test_collect_k_left_direct_ptx_debt_inventory` confirms no direct PTX loads remain for these.

2.  **Does Goal3962 correctly handle the cooperative-launch smoke by dropping the old PTX/RDC-only `--relocatable-device-code=true` option on the CUBIN path, and is that decision supported by pod evidence?**
    Yes. `docs/reports/goal3962_collect_k_direct_cuda_cubin_loader_hardening_2026-06-08.md` clarifies that the `--relocatable-device-code=true` option was intentionally dropped for CUBIN, as it led to an invalid driver image, and reports a successful cooperative-launch smoke test. `tests/goal3962_collect_k_direct_cuda_cubin_loader_hardening_test.py` validates that the option is absent for the cooperative launch kernel's CUBIN compilation and that the cooperative smoke test in `goal3962_collect_k_api_smoke.json` passed.

3.  **Does the Goal3951 inventory now accurately report zero remaining direct `cuModuleLoadData(..., ptx.c_str())` sites under the tracked scanner?**
    Yes. `docs/reports/goal3951_direct_cuda_ptx_loader_debt_inventory_2026-06-08.md` explicitly states, "No remaining direct `cuModuleLoadData(..., ptx.c_str())` debt is currently tracked by this inventory," and "The current remaining driver-loaded PTX count is `0`." This is confirmed by `tests/goal3951_direct_cuda_ptx_loader_debt_inventory_test.py`, which asserts that the list of remaining driver-loaded PTX kernels is empty.

4.  **Does the Goal3962 pod API smoke validly cover row-width-2 small, row-width-2 tiled CUB/merge/final compact, dynamic row-width fallback, and cooperative launch smoke paths?**
    Yes. `docs/reports/goal3962_collect_k_direct_cuda_cubin_loader_hardening_2026-06-08.md` details successful pod API validation for `row_width2_small_bitonic`, `row_width2_tiled_cub_merge_final`, `dynamic_row_width3_fallback`, and cooperative launch smoke paths. The `goal3962_collect_k_api_smoke.json` artifact and its corresponding test `tests/goal3962_collect_k_direct_cuda_cubin_loader_hardening_test.py` corroborate these successful outcomes for all listed paths.

5.  **Is the Goal3963 clean all-app current-scale packet valid evidence from clean pushed commit `b745a7e5` with all 10 rows passing?**
    Yes. `docs/reports/goal3963_current_scale_clean_after_collect_k_cubin_hardening_2026-06-08.md` confirms the source commit `b745a7e5`, a clean working tree, `all_pass: true`, and 10 passing rows. The `goal3963_current_scale_clean_after_collect_k_cubin.json` artifact and `tests/goal3963_current_scale_clean_after_collect_k_cubin_hardening_test.py` both verify these details, including the absence of any claim flag violations for all rows.

6.  **Did any report or artifact accidentally authorize release, public speedup, whole-app, broad RT-core, true-zero-copy, AMD, paper-reproduction, package, automatic-partner-selection, or app-specific native-engine claims?**
    No. All examined documentation (`docs/reports/goal3951_direct_cuda_ptx_loader_debt_inventory_2026-06-08.md`, `docs/reports/goal3962_collect_k_direct_cuda_cubin_loader_hardening_2026-06-08.md`, `docs/reports/goal3963_current_scale_clean_after_collect_k_cubin_hardening_2026-06-08.md`) explicitly includes boundary statements disclaiming such authorizations. The JSON artifacts (`goal3962_collect_k_api_smoke.json`, `goal3963_current_scale_clean_after_collect_k_cubin.json`) and their associated tests (`tests/goal3962_collect_k_direct_cuda_cubin_loader_hardening_test.py`, `tests/goal3963_current_scale_clean_after_collect_k_cubin_hardening_test.py`) consistently show all relevant claim authorization flags set to `false`, and no `claim_flag_violations` were reported.

7.  **What direct CUDA PTX-loader debt remains, if any, after this chain?**
    Zero direct CUDA PTX-loader debt remains after this chain under the tracked scanner. The `docs/reports/goal3951_direct_cuda_ptx_loader_debt_inventory_2026-06-08.md` explicitly states "The current remaining driver-loaded PTX count is `0`." OptiX pipeline PTX is noted to be out of scope for this tracking.
