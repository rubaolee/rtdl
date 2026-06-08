# External Review Request: Goal3933 OptiX Shape-Pair CUBIN Toolchain Repair

Date: 2026-06-08

Please perform a read-only review of Goal3933 on current `main`.

## Files To Inspect

- `docs/reports/goal3933_optix_shape_pair_cubin_toolchain_repair_2026-06-08.md`
- `tests/goal3933_optix_shape_pair_cubin_toolchain_repair_test.py`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `docs/reports/goal3933_optix_shape_pair_cubin_toolchain_repair_pod_2026-06-08/summary_manifest.json`
- `docs/reports/goal3933_optix_shape_pair_cubin_toolchain_repair_pod_2026-06-08/goal3931_evaluation.json`
- `docs/reports/goal3933_optix_shape_pair_cubin_toolchain_repair_pod_2026-06-08/rayjoin_summary.json`
- `docs/reports/goal3933_optix_shape_pair_cubin_toolchain_repair_pod_2026-06-08/rtdbscan_unblocked.json`
- `docs/reports/goal3933_optix_shape_pair_cubin_toolchain_repair_pod_2026-06-08/rtdbscan_blocked.json`

## Questions

1. Does switching `ensure_shape_pair_relation_active_count_device_pipeline` from `compile_to_ptx` to `compile_to_cubin` correctly repair the direct CUDA module loader path without changing the generic engine contract?
2. Do the early closed-shape / shape-pair OptiX CUDA strings remain app-agnostic after replacing host `<math.h>` dependencies with tiny device-local helpers?
3. Does the pod artifact support the claimed engineering conclusion: Goal3927 queue passes, Goal3931 evaluator returns `accept_with_boundary`, RayJoin LSI/overlay hot paths are strong, PIP one-shot still prefers Numba, and RTDBSCAN blocked mode remains slower?
4. Are claim boundaries intact? No release, public speedup, broad RT-core, whole-app speedup, automatic partner selection, true-zero-copy, RayJoin reproduction, or RTDBSCAN reproduction claims should be authorized.
5. Are there any required fixes before this Goal3933 repair can be treated as accepted internal engineering evidence?

## Required Output

Use one of these verdicts only: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Save your review as one of:

- Gemini: `docs/reviews/goal3934_gemini_review_goal3933_optix_cubin_toolchain_repair_2026-06-08.md`
- Claude: `docs/reviews/goal3935_claude_review_goal3933_optix_cubin_toolchain_repair_2026-06-08.md`

Do not authorize release or public claims. This is an internal engineering repair review.
