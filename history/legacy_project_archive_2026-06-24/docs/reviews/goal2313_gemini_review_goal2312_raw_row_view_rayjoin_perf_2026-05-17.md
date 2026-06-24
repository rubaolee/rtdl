# Gemini Review: Goal2312 Prepared Closed-Shape Raw Row View

**Reviewer:** Gemini CLI
**Date:** 2026-05-17
**Goal:** Independent review of Goal2312 Prepared Closed-Shape Raw Row View

## Files Inspected:

- `src/rtdsl/optix_runtime.py`
- `scripts/goal2292_rayjoin_current_prepared_comparison.py`
- `docs/reports/goal2312_prepared_closed_shape_raw_row_view_2026-05-17.md`
- `docs/reports/goal2312_prepared_closed_shape_raw_row_view_pod_2026-05-17.json`
- `tests/goal2312_prepared_closed_shape_raw_row_view_test.py`
- `docs/research/future_version_to_do_list.md`

---

## Review Questions and Answers:

### 1. Does `PreparedOptixPointClosedShapeMembership2D.run_raw(...)` mirror the generic OptiX row-view pattern already used by prepared segment-pair intersection without adding RayJoin/PIP/county/map app-specific engine logic?

Yes, `PreparedOptixPointClosedShapeMembership2D.run_raw(...)` mirrors the generic OptiX row-view pattern. Both `run_raw` methods (for point-closed-shape membership and segment-pair intersection) take packed input, call a specific native function, receive `rows_ptr` and `row_count` from the native call, and construct an `OptixRowView` with appropriate generic `row_type` and `field_names`. The field names used (`"point_id"`, `"shape_id"`, `"membership"`) are generic and do not include app-specific terms like "RayJoin", "PIP", "county", or "map".

### 2. Does the high-level `run(...)` behavior remain compatible with existing dictionary-row callers?

Yes, the high-level `run(...)` behavior remains compatible with existing dictionary-row callers. The `run` method in `PreparedOptixPointClosedShapeMembership2D` calls `self.run_raw(...)` to get an `OptixRowView` and then uses `view.to_dict_rows()` to convert the native row view into a tuple of dictionaries, which is the expected output for existing callers. This pattern is consistent with other high-level `run` methods in the `optix_runtime.py` that also return dictionary rows.

### 3. Does the RayJoin comparison script now measure positive rows through the raw row view, avoiding Python dictionary materialization for the scoped timing?

Yes, the RayJoin comparison script (`scripts/goal2292_rayjoin_current_prepared_comparison.py`) measures positive rows through the raw row view. The `run_pip` function's `run_positive_raw_count` inner function calls `prepared.run_raw(...)` and directly accesses `rows.row_count` without materializing Python dictionaries, thus avoiding the associated overhead for scoped timing measurements.

### 4. Does the pod artifact support the bounded claim: PIP positive rows on the 100k RayJoin-exported stream are now near scalar-count timing, exact count remains 8,686, and LSI remains around 10 ms?

Yes, the pod artifact supports this bounded claim. The `docs/reports/goal2312_prepared_closed_shape_raw_row_view_pod_2026-05-17.json` and `docs/reports/goal2312_prepared_closed_shape_raw_row_view_2026-05-17.md` report the following:
- PIP positive raw row view median time: 0.008657 seconds.
- PIP scalar count median time: 0.008476 seconds.
These times are indeed very close, supporting the "near scalar-count timing" claim. Both PIP metrics also report an exact count of 8,686 rows, confirming the "exact count remains 8,686" claim. Lastly, the LSI raw witness rows median time is 0.010123 seconds, which is around 10 ms, supporting the "LSI remains around 10 ms" claim.

### 5. Are the claim boundaries correctly narrow: no RTDL-beats-RayJoin claim, no full RayJoin paper reproduction claim, no whole-app speedup, no true zero-copy/device-resident continuation claim, and no v2.0 release authorization?

Yes, the claim boundaries are correctly narrow. The `docs/reports/goal2312_prepared_closed_shape_raw_row_view_2026-05-17.md` report explicitly lists these points under "This report does not claim:", ensuring the boundaries are clear and narrow. This is further supported by the `claim_boundary` entry in `docs/reports/goal2312_prepared_closed_shape_raw_row_view_pod_2026-05-17.json` and verified by `test_report_keeps_claim_boundary` in `tests/goal2312_prepared_closed_shape_raw_row_view_test.py`.

---

## Verdict:

accept-with-boundary
