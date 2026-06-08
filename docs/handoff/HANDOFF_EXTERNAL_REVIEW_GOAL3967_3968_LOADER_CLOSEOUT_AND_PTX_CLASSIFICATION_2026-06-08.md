# Handoff: External Review For Goals3967-3968 Loader Closeout And PTX Classification

Date: 2026-06-08

Please perform an independent read-only review of Goals3967-3968.

## Commits

- `339b69d9` Goal3967 close direct CUDA loader lane
- `e383c4e4` Goal3968 classify remaining OptiX PTX callsites

## Files To Inspect

- `docs/reports/goal3967_direct_cuda_loader_hardening_lane_closeout_2026-06-08.md`
- `tests/goal3967_direct_cuda_loader_hardening_lane_closeout_test.py`
- `docs/reports/goal3968_remaining_ptx_callsite_classification_after_direct_loader_closeout_2026-06-08.md`
- `tests/goal3968_remaining_ptx_callsite_classification_after_direct_loader_closeout_test.py`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- prior review files `docs/reviews/goal3956*`, `goal3957*`, `goal3960*`,
  `goal3961*`, `goal3964*`, and `goal3965*`

## Questions To Answer

1. Does Goal3967 accurately close the direct CUDA driver-module PTX loader lane
   without overclaiming release, speedup, true-zero-copy, AMD, package, paper
   reproduction, automatic partner selection, or app-specific engine claims?
2. Does the closeout correctly distinguish the tracked direct-loader debt from
   intentional OptiX pipeline PTX?
3. Does Goal3968 correctly classify all remaining `compile_to_ptx(...)`
   workload call sites as OptiX pipeline-build inputs, and are the counts
   (`57` workload calls, `1` helper definition, `0` direct driver PTX payload
   loads) accurate?
4. Are the Goal3967/3968 tests strong enough to guard the distinction between
   CUDA driver module payloads and OptiX program-module PTX?
5. What material risk remains before we leave this loader-hardening lane?

## Required Output

Use the verdict vocabulary `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

- Claude should write:
  `docs/reviews/goal3969_claude_review_goal3967_3968_loader_closeout_ptx_classification_2026-06-08.md`
- Gemini should write:
  `docs/reviews/goal3970_gemini_review_goal3967_3968_loader_closeout_ptx_classification_2026-06-08.md`

Please keep this read-only except for writing the requested review file.
