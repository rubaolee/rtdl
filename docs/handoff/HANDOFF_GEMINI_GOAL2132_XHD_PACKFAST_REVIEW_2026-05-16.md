# Handoff: Gemini Review for Goal2131/Goal2132 X-HD Packfast Hausdorff

Please perform an independent Gemini review of the Goal2131 and Goal2132 work.

Scope:

- `docs/reports/goal2131_xhd_seeded_pruned_hausdorff_2026-05-16.md`
- `docs/reports/goal2132_xhd_seeded_pruned_packfast_a5000_perf_2026-05-16.md`
- `docs/reports/goal2131_public_pod_a5000_seeded_pruned_sweep_packfast/*.json`
- `tests/goal2131_xhd_seeded_pruned_hausdorff_test.py`
- `tests/goal2132_xhd_seeded_pruned_packfast_a5000_perf_test.py`
- `examples/rtdl_hausdorff_v2_function.py`
- `scripts/goal2126_public_hausdorff_dataset_perf.py`
- `src/rtdsl/embree_runtime.py`
- `src/rtdsl/optix_runtime.py`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`

Questions to answer:

1. Does the new native surface remain generic and app-agnostic?
2. Is the exact Hausdorff argument valid: sample lower-bound witness plus threshold flags plus exact unsafe-subset reduction?
3. Does the vectorized `pack_points` change preserve compatibility while removing per-row ctypes packing for column inputs?
4. Do the A5000 artifacts support the narrow claim that RTDL/OptiX seeded-pruned beats optimized grouped CuPy on these public projected-XY cases?
5. Are the claim boundaries precise enough: no all-CUDA, no X-HD paper-dataset equivalence, no 3D surface claim, no broad release claim?

Please write the review to:

`docs/reviews/goal2133_gemini_review_goal2131_2132_xhd_packfast_hd_2026-05-16.md`

Use verdicts from this set only: `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`.
