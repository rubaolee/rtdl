# Review of Goal2046: CuPy Witness Continuation Surface

**Reviewer:** Gemini CLI Agent
**Date:** 2026-05-14

## Verdict

`accept-with-boundary`

## Review Summary

Goal2046 introduces CuPy-facing witness-continuation surfaces, mirroring the NumPy reference primitives from Goal2044. This work provides `cupy_group_topk`, `cupy_group_argmin_then_global_argmax_with_witness`, and `directed_hausdorff_2d_cupy_columns`. The primary purpose is to establish a contract/runtime surface for future pod validation, explicitly not for release performance evidence. The design maintains app-agnosticism for the core primitives, with `directed_hausdorff_2d_cupy_columns` acting as an application-specific adapter. Explicit boundaries are clearly defined, mitigating risks associated with accepting this surface before full pod runtime evidence.

## Responses to Review Questions

1.  **Does this preserve app-agnostic partner-continuation design?**
    Yes, the design appears to preserve app-agnostic partner-continuation. The core CuPy functions (`cupy_group_topk`, `cupy_group_argmin_then_global_argmax_with_witness`) are generic primitives, and `directed_hausdorff_2d_cupy_columns` acts as an adapter, building upon these generic primitives for a specific application (directed Hausdorff 2D). This separation of concerns maintains the app-agnostic nature of the underlying continuation mechanisms.

2.  **Is it reasonable to accept this as a bounded CuPy surface before pod runtime evidence?**
    Yes, it is reasonable to accept this as a bounded CuPy surface before pod runtime evidence. The report clearly states its purpose as a contract/runtime surface for *future* pod validation and explicitly clarifies that it is *not* for release performance evidence or making large-scale speed claims. The functional correctness is tested against NumPy, providing a baseline.

3.  **Are the boundaries clear enough: no pod evidence, no OptiX zero-copy candidate-row handoff, no large-scale speed claim, no v2.0 release authorization?**
    Yes, the boundaries are very clear. The Goal2046 report explicitly lists these limitations, and the `directed_hausdorff_2d_cupy_columns` function itself includes metadata reinforcing these restrictions. The test suite also verifies that these boundary statements are present in the report.

4.  **What should be the next pod validation step?**
    The next pod validation steps are clearly outlined in the Goal2046 report:
    1.  Verify `directed_hausdorff_2d_cupy_columns` correctness against the NumPy reference.
    2.  Perform exact Hausdorff application timing using `partner_exact --partner cupy`.
    3.  Integrate and validate with future same-contract OptiX candidate-row handoff once it becomes available.
