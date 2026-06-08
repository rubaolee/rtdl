# Handoff: External Review For Goals3962-3963 Collect-K CUBIN / Zero Direct PTX

Date: 2026-06-08

Please perform an independent read-only review of Goals3962-3963.

## Commits

- `b745a7e5` Goal3962 harden collect-k CUDA loaders
- `11638bff` Goal3963 clean all-app current-scale after Goal3962

## Files To Inspect

- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `docs/reports/goal3951_direct_cuda_ptx_loader_debt_inventory_2026-06-08.md`
- `docs/reports/goal3962_collect_k_direct_cuda_cubin_loader_hardening_2026-06-08.md`
- `docs/reports/goal3962_collect_k_direct_cuda_cubin_loader_hardening_2026-06-08/goal3962_collect_k_api_smoke.json`
- `docs/reports/goal3963_current_scale_clean_after_collect_k_cubin_hardening_2026-06-08.md`
- `docs/reports/goal3963_current_scale_clean_after_collect_k_cubin_hardening_2026-06-08/goal3963_current_scale_clean_after_collect_k_cubin.json`
- `tests/goal3951_direct_cuda_ptx_loader_debt_inventory_test.py`
- `tests/goal3962_collect_k_direct_cuda_cubin_loader_hardening_test.py`
- `tests/goal3963_current_scale_clean_after_collect_k_cubin_hardening_test.py`

## Questions To Answer

1. Does Goal3962 correctly convert the remaining collect-k direct CUDA helper
   module loaders to `compile_to_cubin(...)` plus
   `cuModuleLoadData(..., cubin.data())`?
2. Does Goal3962 correctly handle the cooperative-launch smoke by dropping the
   old PTX/RDC-only `--relocatable-device-code=true` option on the CUBIN path,
   and is that decision supported by pod evidence?
3. Does the Goal3951 inventory now accurately report zero remaining direct
   `cuModuleLoadData(..., ptx.c_str())` sites under the tracked scanner?
4. Does the Goal3962 pod API smoke validly cover row-width-2 small, row-width-2
   tiled CUB/merge/final compact, dynamic row-width fallback, and cooperative
   launch smoke paths?
5. Is the Goal3963 clean all-app current-scale packet valid evidence from clean
   pushed commit `b745a7e5` with all 10 rows passing?
6. Did any report or artifact accidentally authorize release, public speedup,
   whole-app, broad RT-core, true-zero-copy, AMD, paper-reproduction, package,
   automatic-partner-selection, or app-specific native-engine claims?
7. What direct CUDA PTX-loader debt remains, if any, after this chain?

## Required Output

Use the verdict vocabulary `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

- Claude should write:
  `docs/reviews/goal3964_claude_review_goal3962_3963_collect_k_cubin_zero_direct_ptx_2026-06-08.md`
- Gemini should write:
  `docs/reviews/goal3965_gemini_review_goal3962_3963_collect_k_cubin_zero_direct_ptx_2026-06-08.md`

Please keep this read-only except for writing the requested review file.
