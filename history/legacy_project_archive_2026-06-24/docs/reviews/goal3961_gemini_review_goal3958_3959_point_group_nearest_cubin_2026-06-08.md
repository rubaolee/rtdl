# Independent Gemini Review for Goals3958-3959 Point-Group-Nearest CUBIN Hardening

## Date
2026-06-08

## Reviewer
Gemini

## Verdict
accept

## Questions and Answers

### 1. Does Goal3958 correctly convert the point-group-nearest split/reduce CUDA helper module loaders to `compile_to_cubin(...)` plus `cuModuleLoadData(..., cubin.data())`?
Yes, Goal3958 correctly converts the point-group-nearest split/reduce CUDA helper module loaders to `compile_to_cubin(...)` plus `cuModuleLoadData(..., cubin.data())`, as confirmed by the Goal3958 report (`docs/reports/goal3958_point_group_nearest_direct_cuda_cubin_loader_hardening_2026-06-08.md`) and the dedicated unit test (`tests/goal3958_point_group_nearest_direct_cuda_cubin_loader_hardening_test.py`).

### 2. Does Goal3958 preserve the OptiX point-group RT probe pipeline PTX paths that feed `build_pipeline(...)`?
Yes, Goal3958 preserves the OptiX point-group RT probe pipeline PTX paths that feed `build_pipeline(...)`, as stated in the Goal3958 report and validated by the corresponding unit test.

### 3. Is the Goal3958 direct API pod smoke valid evidence for the split-columns helper, max-reduce helper, and active-frontier reduce reuse path?
Yes, the Goal3958 direct API pod smoke is valid evidence for the split-columns helper, max-reduce helper, and active-frontier reduce reuse path. This is confirmed by the Goal3958 report, the content of `docs/reports/goal3958_point_group_nearest_direct_cuda_cubin_loader_hardening_2026-06-08/goal3958_point_group_nearest_api_smoke.json` (which shows all 7 API checks passing), and its unit test (`tests/goal3958_point_group_nearest_direct_cuda_cubin_loader_hardening_test.py`).

### 4. Does Goal3951 now accurately report the remaining direct driver-loaded PTX debt as 9 collect-k sites only?
Yes, Goal3951 now accurately reports the remaining direct driver-loaded PTX debt as 9 `collect-k` sites only. This is explicitly stated in the "Follow-Up" section of `docs/reports/goal3951_direct_cuda_ptx_loader_debt_inventory_2026-06-08.md` and confirmed by the `tests/goal3951_direct_cuda_ptx_loader_debt_inventory_test.py` unit test.

### 5. Is the Goal3959 clean all-app current-scale packet valid evidence from clean pushed commit `57a27e52` with all 10 rows passing?
Yes, the Goal3959 clean all-app current-scale packet is valid evidence from clean pushed commit `57a27e52` with all 10 rows passing. This is detailed in the Goal3959 report (`docs/reports/goal3959_current_scale_clean_after_point_group_nearest_cubin_hardening_2026-06-08.md`), confirmed by its JSON artifact (`docs/reports/goal3959_current_scale_clean_after_point_group_nearest_cubin_hardening_2026-06-08/goal3959_current_scale_clean_after_point_group_nearest_cubin.json`), and validated by its unit test (`tests/goal3959_current_scale_clean_after_point_group_nearest_cubin_hardening_test.py`).

### 6. Did any report or artifact accidentally authorize release, public speedup, whole-app, broad RT-core, true-zero-copy, AMD, paper-reproduction, package, automatic-partner-selection, or app-specific native-engine claims?
No, none of the reports or artifacts accidentally authorized release, public speedup, whole-app, broad RT-core, true-zero-copy, AMD, paper-reproduction, package, automatic-partner-selection, or app-specific native-engine claims. This is explicitly stated in the boundary sections of both Goal3958 and Goal3959 reports, and consistently confirmed by their respective JSON artifacts and unit tests.

### 7. What remains as the next direct CUDA loader debt after this chain?
After this chain of goals, the remaining direct CUDA loader debt consists of 9 `collect-k` sites, all related to various `collect_k` kernels, as listed in the `docs/reports/goal3951_direct_cuda_ptx_loader_debt_inventory_2026-06-08.md` report. These include kernels such as `collect_k_cooperative_launch_smoke_kernel.cu`, `collect_k_bounded_i64_row_width2_sort_kernel.cu`, and `collect_k_bounded_i64_kernel.cu`.
