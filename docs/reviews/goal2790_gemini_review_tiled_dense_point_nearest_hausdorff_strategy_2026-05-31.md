# Independent Gemini Review For Goal2790

Date: 2026-05-31

## Review of Goal2790: Tiled Dense Point-Nearest Hausdorff Strategy

### 1. Does the Triton continuation file remain generic and app-name-free?
Yes, the `src/rtdsl/triton_partner_continuation.py` file remains generic and app-name-free. It introduces `run_triton_dense_point_nearest_2d_tiled` and `TRITON_DENSE_POINT_NEAREST_2D_TILED_ADAPTER_KERNEL` which are generic operations. The code does not contain references to "Hausdorff" or any other application-specific names. This was also confirmed by an explicit assertion in `tests/goal2790_hausdorff_tiled_dense_point_nearest_test.py`.

### 2. Does the tiled strategy correctly compose generic point-nearest tile witnesses, `grouped_argmin_f64`, and `grouped_argmax_f64`?
Yes, the tiled strategy correctly composes these operations. The `run_triton_dense_point_nearest_2d_tiled` function in `src/rtdsl/triton_partner_continuation.py` generates per-query per-tile nearest witnesses. These witnesses are then reduced using `run_triton_grouped_argmin_f64`. Subsequently, `directed_hausdorff_2d_partner_columns` in `src/rtdsl/partner_adapters.py` uses `run_triton_grouped_argmax_f64` on the results to find the directed Hausdorff witness. The logical flow and composition are appropriate.

### 3. Does it preserve exact directed Hausdorff distance and witness identity against Torch?
Yes, the implementation preserves exact directed Hausdorff distance and witness identity against Torch. The unit test `tests/goal2790_hausdorff_tiled_dense_point_nearest_test.py` explicitly verifies this by comparing `nearest_distances`, `source_id`, `target_id`, and `distance` against the Torch reference implementation. The test passes, and the POD artifact `goal2790_tiled_dense_point_nearest_hausdorff_pod_69_30_85_171_2026-05-31.json` confirms that `best_tiled_distance_error` is `0.0` and `best_tiled_source_id_match` and `best_tiled_target_id_match` are `true` for all measured scenarios.

### 4. Does the timing report honestly state the thresholded result: slower at 2K/4K/8K, faster at measured 16K, and not a blanket speedup claim?
Yes, the timing report in `docs/reports/goal2790_tiled_dense_point_nearest_hausdorff_strategy_2026-05-31.md` is honest and accurately reflects the thresholded results. It clearly states that the tiled Triton route is slower than Torch for small and mid dense shapes (2K/4K/8K) and becomes faster only at the measured 16K x 16K shape. The report explicitly avoids making a blanket speedup claim and notes that it is not yet a public speedup claim or a release path. The provided timing table and POD artifact data support these statements.

### 5. Are RT-core, true zero-copy, whole-app, public speedup, automatic-selection, and v2.5 release claims still blocked?
Yes, all these claims remain blocked. The "Boundary" section of the report clearly lists all unauthorized claims, including public speedup, RT-core speedup, true zero-copy, whole-app speedup, v2.5 release readiness, and automatic partner selection. The POD artifact also explicitly sets these claim authorizations to `false`. The `test_report_and_artifact_record_boundary` test in the unit test file further validates these boundaries.

### Verdict
`accept-with-boundary`

Goal2790 is accepted as internal v2.5 preview evidence. The tiled strategy provides a promising performance direction for large shapes, fulfilling its purpose as an internal preview. The implementation is correct, generic, and well-documented with clear boundaries on its authorized claims.
