# Handoff: External Review For Goals3951-3955 Direct CUDA CUBIN Debt Chain

Date: 2026-06-08

Please perform an independent review of the direct CUDA PTX-loader debt cleanup
chain covering Goals3951-3955.

## Commits

- `83c177c0` Goal3951 direct CUDA PTX loader debt inventory
- `9c13d1c6` Goal3952 grouped + segment-pair direct CUDA CUBIN hardening
- `d4b6e304` Goal3953 clean all-app current-scale after Goal3952
- `d9c736c5` Goal3954 partner triangle/ray pack direct CUDA CUBIN hardening
- `372a391e` Goal3955 clean all-app current-scale after Goal3954

## Files To Inspect

- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `docs/reports/goal3951_direct_cuda_ptx_loader_debt_inventory_2026-06-08.md`
- `docs/reports/goal3952_grouped_and_segment_pair_direct_cuda_cubin_loader_hardening_2026-06-08.md`
- `docs/reports/goal3953_current_scale_clean_after_grouped_segment_cubin_hardening_2026-06-08.md`
- `docs/reports/goal3954_partner_pack_direct_cuda_cubin_loader_hardening_2026-06-08.md`
- `docs/reports/goal3955_current_scale_clean_after_partner_pack_cubin_hardening_2026-06-08.md`
- `tests/goal3951_direct_cuda_ptx_loader_debt_inventory_test.py`
- `tests/goal3952_grouped_and_segment_pair_direct_cuda_cubin_loader_hardening_test.py`
- `tests/goal3953_current_scale_clean_after_grouped_segment_cubin_hardening_test.py`
- `tests/goal3954_partner_pack_direct_cuda_cubin_loader_hardening_test.py`
- `tests/goal3955_current_scale_clean_after_partner_pack_cubin_hardening_test.py`

## Questions To Answer

1. Do the Goal3952 and Goal3954 native changes correctly convert the targeted
   direct CUDA helpers from `compile_to_ptx(...)` plus `ptx.c_str()` to
   `compile_to_cubin(...)` plus `cubin.data()`?
2. Do these goals leave OptiX pipeline PTX generation untouched?
3. Does the Goal3951 inventory accurately report the remaining direct
   driver-loaded PTX debt as 12 sites after Goal3954?
4. Are the Goal3952 and Goal3954 pod smoke artifacts valid, narrow, and
   claim-boundary-clean?
5. Are the Goal3953 and Goal3955 clean all-app current-scale packets valid
   evidence from clean pushed commits (`9c13d1c6` and `d9c736c5`) with all 10
   benchmark rows passing?
6. Are there any release/public-speedup/whole-app/broad-RT-core/zero-copy/AMD/
   paper-reproduction/automatic-partner-selection claims accidentally
   authorized by these reports or artifacts?
7. What remains as the next direct CUDA loader debt after this chain?

## Required Output

Use the verdict vocabulary `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

- Claude should write:
  `docs/reviews/goal3956_claude_review_goal3951_3955_direct_cuda_cubin_debt_chain_2026-06-08.md`
- Gemini should write:
  `docs/reviews/goal3957_gemini_review_goal3951_3955_direct_cuda_cubin_debt_chain_2026-06-08.md`

Please keep this read-only except for writing the requested review file.
