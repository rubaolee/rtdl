---

## Findings

**1. `result_mode="raw"` as a first-class path**

Confirmed. `run_embree` at line 418 now validates `result_mode` up front, rejects unknown values, and routes any `result_mode="raw"` call — including ordinary (non-packed) record inputs — through `prepare_embree(...).bind(...).run_raw()` (lines 429–431). This is no longer a packed-input special case; unpacked inputs are packed on the fly.

**2. Prepared/raw coverage beyond lsi/pip**

Confirmed. `PreparedEmbreeKernel` at lines 192–202 now admits all six predicates: `segment_intersection`, `point_in_polygon`, `overlay_compose`, `ray_triangle_hit_count`, `segment_polygon_hitcount`, `point_nearest_segment`. `PreparedEmbreeExecution.run_raw()` dispatches all six. `pack_triangles` and `pack_rays` are new and exported.

**3. Correctness claims supported by tests**

Confirmed. `test_raw_result_mode_matches_dict_rows_for_all_workloads` checks all six workloads against the ordinary dict path using `assertEqual`. `test_prepared_raw_supports_goal18_extended_workloads` checks the four new workloads via the prepared path. `report_smoke_test` checks `raw_matches_dict` is `True` for lsi and pip in the generated JSON. The report itself shows `raw matches dict: True` on all six.

**4. Native performance claims limited honestly**

Confirmed. `NATIVE_BASELINE_WORKLOADS = {"lsi", "pip"}` in the benchmark script gates all `goal15_native_total_sec` / `gap_*_vs_native` fields. The four extended workloads carry no native comparison fields. The report's Interpretation section states this explicitly. The benchmark does not report gap-to-native for overlay, ray_tri_hitcount, segment_polygon_hitcount, or point_nearest_segment.

**5. Blockers**

None identified. The `gap_raw_vs_native` values for lsi (0.10x) and pip (0.12x) mean the raw path is *faster* than the native lower-bound at these dataset sizes, which is a known artifact of minimal/cold-start datasets — the report does not overclaim from these numbers. The overlay `prepared_raw_hot_median` (0.0000185 s) being slightly slower than `prepared_dict_hot_median` (0.0000142 s) at the minimal dataset size is unremarkable and not claimed otherwise.

---

## Decision

All five acceptance criteria from the goal spec are met:
- DSL surface unchanged
- `result_mode="raw"` is first-class and ergonomically reachable from `run_embree`
- prepared/raw covers the full current local Embree workload surface (lsi, pip, overlay, ray_tri_hitcount, segment_polygon_hitcount, point_nearest_segment)
- correctness parity demonstrated by direct equality checks across all six workloads
- native-comparison claims limited to lsi/pip throughout

---

Goal 18 complete by consensus
