# External Review Handoff: Goals3942-3943 FRN3D CUBIN Repair and Clean Scale Refresh

Please perform a read-only independent review of the Goal3942/Goal3943 work on
RTDL `main`.

## Files To Read

- `docs/reports/goal3942_frn3d_direct_cuda_cubin_toolchain_repair_2026-06-08.md`
- `tests/goal3942_frn3d_direct_cuda_cubin_toolchain_repair_test.py`
- `docs/reports/goal3942_frn3d_direct_cuda_cubin_toolchain_repair_2026-06-08/rtnn_frn3d_cubin.json`
- `docs/reports/goal3943_current_scale_clean_after_frn3d_cubin_repair_2026-06-08.md`
- `tests/goal3943_current_scale_clean_after_frn3d_cubin_repair_test.py`
- `docs/reports/goal3943_current_scale_clean_after_frn3d_cubin_repair_2026-06-08/goal3943_current_scale_clean_d792b037.json`
- `src/native/optix/rtdl_optix_workloads.cpp`
- optionally `docs/reports/goal3938_current_benchmark_route_decision_registry_2026-06-08.md` and `src/rtdsl/current_benchmark_route_decisions.py` to verify the AMD claim-boundary follow-up.

## Review Questions

1. Does Goal3942 correctly repair the fixed-radius 3D direct CUDA module path by
   moving only the two FRN3D loaders from PTX JIT to CUBIN loading?
2. Does the Goal3942 pod artifact prove the previously failing RTNN row runs
   after the repair, without overclaiming performance?
3. Does Goal3943 provide clean current-scale evidence from commit `d792b037`
   with `all_pass=true`, 10/10 JSON-pass rows, clean working tree, and no claim
   flag violations?
4. Are the claim boundaries intact: no release, public speedup, whole-app
   acceleration, broad RT-core, true-zero-copy, automatic partner/backend
   selection, AMD performance, paper reproduction, package-install, or
   app-specific native-engine logic claims?
5. Is there any required fix before treating Goals3942/3943 as accepted internal
   toolchain and current-scale evidence?

## Required Output

Write the review to one of these paths:

- Claude: `docs/reviews/goal3944_claude_review_goal3942_3943_frn3d_cubin_clean_scale_2026-06-08.md`
- Gemini: `docs/reviews/goal3945_gemini_review_goal3942_3943_frn3d_cubin_clean_scale_2026-06-08.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.
