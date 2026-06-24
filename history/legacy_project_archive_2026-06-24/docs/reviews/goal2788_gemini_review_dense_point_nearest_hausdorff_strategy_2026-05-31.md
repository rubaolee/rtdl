# Independent Gemini Review for Goal2788

Date: 2026-05-31

## Verdict

`accept-with-boundary`

Goal2788 is accepted as a design improvement over Goal2787 and as negative selection evidence. The fused dense point-nearest strategy is correct and better than materializing dense score rows, but it still does not beat Torch for the tested dense Hausdorff shapes.

## Review Questions Addressed

### 1. Does Goal2788 keep the Triton continuation substrate generic, with no Hausdorff/X-HD/app vocabulary in `src/rtdsl/triton_partner_continuation.py`?

Yes, the Triton continuation substrate remains generic. The file `src/rtdsl/triton_partner_continuation.py` defines generic mathematical or data manipulation primitives (e.g., `segmented_sum_f64`, `grouped_argmin_f64`, `dense_point_nearest_2d_adapter_kernel`). While `TRITON_DENSE_POINT_NEAREST_2D_ADAPTER_KERNEL` is included, its implementation (`run_triton_dense_point_nearest_2d`) operates on generic point coordinates and IDs without specific Hausdorff, X-HD, or other application-level vocabulary.

### 2. Is `dense_point_nearest_2d_adapter_kernel` correctly treated as a generic adapter strategy under the existing grouped-argmin style witness contract, rather than being promoted as a new app-specific continuation operation?

Yes, `dense_point_nearest_2d_adapter_kernel` is correctly treated as a generic adapter strategy. In `src/rtdsl/partner_adapters.py`, the `directed_hausdorff_2d_partner_columns` function uses this strategy by calling `run_triton_dense_point_nearest_2d` to find nearest neighbors (a generic spatial operation). The output is then fed into `run_triton_grouped_argmax_f64`, which is a generic grouped argmax operation, to determine the overall farthest nearest neighbor, consistent with the grouped-argmin style witness contract. The adapter's metadata in `triton_partner_continuation.py` also indicates `logical_operation: TRITON_GROUPED_ARGMIN_F64_OPERATION`, confirming its role as an adapter for existing generic operations, not a new app-specific primitive.

### 3. Does `directed_hausdorff_2d_partner_columns(..., partner="triton", triton_strategy="dense_point_nearest")` preserve exact directed Hausdorff distance and witness identity compared with the Torch branch?

Yes, the `dense_point_nearest` Triton strategy preserves exact directed Hausdorff distance and witness identity compared with the Torch branch. The test `test_directed_hausdorff_dense_strategy_matches_torch_when_cuda_available` in `tests/goal2788_hausdorff_dense_point_nearest_triton_strategy_test.py` explicitly verifies numerical closeness of `nearest_distances`, equality of `source_id` and `target_id` (witness identity), and near-equality of the final directed Hausdorff distance, confirming functional correctness.

### 4. Does the pod evidence honestly show both sides of the result: Goal2788 is faster than the Goal2787 generic score-row Triton route, but still 3.77x to 30.73x slower than Torch on measured RTX A5000 dense shapes?

Yes, the pod evidence presented in `docs/reports/goal2788_dense_point_nearest_hausdorff_strategy_2026-05-31.md` and `docs/reports/goal2788_pod_artifacts/goal2788_dense_point_nearest_hausdorff_pod_69_30_85_171_2026-05-31.json` honestly shows both sides of the result. The "Pod Timing" table clearly indicates:
*   Goal2788 is faster than Goal2787, with "Dense / Generic" ratios ranging from 0.458x to 0.816x.
*   Goal2788 is still slower than Torch, with "Dense / Torch" ratios ranging from 3.774x to 30.720x.
The report's narrative also explicitly states these findings.

### 5. Do the partner-selection and app-migration guidance files correctly block automatic Triton selection for the dense Hausdorff-style witness-reduction shapes?

Yes, both `src/rtdsl/v2_5_partner_selection_guidance.py` and `src/rtdsl/v2_5_triton_app_migration.py` correctly block automatic Triton selection.
*   `v2_5_partner_selection_guidance.py` includes a `V25PartnerSelectionGuidanceRow` for Goal2788's workload shape, explicitly recommending "Do not auto-select Triton..." and validating that `auto_select_measured_partner_allowed` is `False`.
*   `v2_5_triton_app_migration.py` in the `hausdorff_xhd` plan notes that "Goal2787 and Goal2788 both block blind Triton auto-selection for dense exact Hausdorff-style witness reduction." and advises to "Keep optimized Torch/CuPy/CUDA or another explicitly selected same-contract partner..."

### 6. Are all claim boundaries still blocked?

Yes, all claim boundaries are still blocked. The "Boundary" section in `docs/reports/goal2788_dense_point_nearest_hausdorff_strategy_2026-05-31.md` explicitly states that this goal does not authorize public speedup claims, RT-core speedup claims, true zero-copy claims, whole-app speedup claims, v2.5 release readiness, a Hausdorff-specific native or Triton continuation primitive, or auto-selecting Triton for dense exact Hausdorff-style witness reduction. The corresponding JSON artifact also confirms these claims as `false`.
