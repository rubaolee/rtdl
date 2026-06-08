# Handoff: External Review For Goals3958-3959 Point-Group-Nearest CUBIN Hardening

Date: 2026-06-08

Please perform an independent read-only review of Goals3958-3959.

## Commits

- `57a27e52` Goal3958 harden point group nearest CUDA loaders
- `b820b986` Goal3959 clean all-app current-scale after Goal3958

## Files To Inspect

- `src/native/optix/rtdl_optix_workloads.cpp`
- `docs/reports/goal3951_direct_cuda_ptx_loader_debt_inventory_2026-06-08.md`
- `docs/reports/goal3958_point_group_nearest_direct_cuda_cubin_loader_hardening_2026-06-08.md`
- `docs/reports/goal3958_point_group_nearest_direct_cuda_cubin_loader_hardening_2026-06-08/goal3958_point_group_nearest_api_smoke.json`
- `docs/reports/goal3959_current_scale_clean_after_point_group_nearest_cubin_hardening_2026-06-08.md`
- `docs/reports/goal3959_current_scale_clean_after_point_group_nearest_cubin_hardening_2026-06-08/goal3959_current_scale_clean_after_point_group_nearest_cubin.json`
- `tests/goal3951_direct_cuda_ptx_loader_debt_inventory_test.py`
- `tests/goal3958_point_group_nearest_direct_cuda_cubin_loader_hardening_test.py`
- `tests/goal3959_current_scale_clean_after_point_group_nearest_cubin_hardening_test.py`

## Questions To Answer

1. Does Goal3958 correctly convert the point-group-nearest split/reduce CUDA
   helper module loaders to `compile_to_cubin(...)` plus
   `cuModuleLoadData(..., cubin.data())`?
2. Does Goal3958 preserve the OptiX point-group RT probe pipeline PTX paths that
   feed `build_pipeline(...)`?
3. Is the Goal3958 direct API pod smoke valid evidence for the split-columns
   helper, max-reduce helper, and active-frontier reduce reuse path?
4. Does Goal3951 now accurately report the remaining direct driver-loaded PTX
   debt as 9 collect-k sites only?
5. Is the Goal3959 clean all-app current-scale packet valid evidence from clean
   pushed commit `57a27e52` with all 10 rows passing?
6. Did any report or artifact accidentally authorize release, public speedup,
   whole-app, broad RT-core, true-zero-copy, AMD, paper-reproduction, package,
   automatic-partner-selection, or app-specific native-engine claims?
7. What remains as the next direct CUDA loader debt after this chain?

## Required Output

Use the verdict vocabulary `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

- Claude should write:
  `docs/reviews/goal3960_claude_review_goal3958_3959_point_group_nearest_cubin_2026-06-08.md`
- Gemini should write:
  `docs/reviews/goal3961_gemini_review_goal3958_3959_point_group_nearest_cubin_2026-06-08.md`

Please keep this read-only except for writing the requested review file.
