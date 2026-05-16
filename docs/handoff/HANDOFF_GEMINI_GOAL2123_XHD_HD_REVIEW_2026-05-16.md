# Gemini Handoff: Review Goal2121-2123 X-HD-Style RTDL/OptiX Hausdorff Work

Please perform an independent read-only review and write your review to:

`docs/reviews/goal2124_gemini_review_goal2121_2123_xhd_hausdorff_optix_2026-05-16.md`

## Context

The user asked us to use techniques from the X-HD paper to enhance the RTDL/OptiX Hausdorff distance program with the goal of outperforming pure CUDA-core solutions on the same datasets used in the X-HD paper.

The current work does not yet run the exact X-HD paper datasets because the cloned X-HD repository contains scripts and dataset names but not the large referenced data files. However, it does add two generic RTDL/OptiX primitives and validates a large synthetic crossover against a CuPy exact all-pairs baseline on an A5000 pod.

## Files To Read

- `docs/reports/goal2121_xhd_point_group_hausdorff_optix_enhancement_2026-05-16.md`
- `docs/reports/goal2122_xhd_grouped_hausdorff_pod_perf_2026-05-16.md`
- `docs/reports/goal2123_xhd_point_group_nearest_reduction_2026-05-16.md`
- `docs/reports/goal2123_pod_grouped_reduced_hd_perf_2026-05-16.json`
- `tests/goal2121_xhd_point_group_hausdorff_optix_enhancement_test.py`
- `tests/goal2122_xhd_grouped_hausdorff_pod_perf_test.py`
- `tests/goal2123_xhd_point_group_nearest_reduction_test.py`
- `examples/rtdl_hausdorff_v2_function.py`
- `examples/rtdl_hausdorff_v2_language_lab.py`
- `src/rtdsl/optix_runtime.py`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`

## Specific Questions

1. Does the native OptiX ABI remain app-agnostic? In particular, verify that the new native symbols are generic point-group / nearest-witness / max-distance-reduction names and do not introduce Hausdorff, X-HD, dataset, GIS, or app-specific engine customization.
2. Is the Python Hausdorff app correctly using RTDL as a language/runtime layer while keeping app-specific logic in Python?
3. Do the reports avoid overclaiming? They should allow the large-synthetic A5000 crossover but keep the exact-X-HD-paper-dataset claim as `needs-more-evidence`.
4. Does Goal2123 fairly identify the remaining X-HD gaps: estimator pruning, heavy-cell CUDA fallback, and device worklist?
5. Does the pod evidence support the narrow conclusion that reduced RTDL/OptiX beats CuPy exact all-pairs continuation at 131,072+ synthetic points per set on this A5000 run?

## Required Verdict Format

Use the project verdict vocabulary:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please include:

- A clear verdict for Goal2121/2122/2123.
- A separate verdict for "outperforms pure CUDA on large synthetic sets".
- A separate verdict for "outperforms pure CUDA on the same X-HD paper datasets".
- Any blockers or recommended follow-up tests.

This must be a read-only review except for writing the requested review file.
