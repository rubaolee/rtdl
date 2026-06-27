# Goal 18 Implementation Report

## Scope

Goal 18 continues the low-overhead runtime work from Goal 17.

This slice keeps the Python-like DSL unchanged and focuses on the runtime path:

- make `run_embree(..., result_mode="raw")` a first-class execution mode
- extend prepared/raw execution across the currently supported local Embree workloads
- add packed support for the remaining geometry kinds needed by those workloads
- add validation and reporting for the extended path

## Implemented Changes

### Runtime

Updated [embree_runtime.py](/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py):

- added `PackedTriangles`
- added `PackedRays`
- added `pack_triangles(...)`
- added `pack_rays(...)`
- extended `PreparedEmbreeKernel` support to:
  - `overlay_compose`
  - `ray_triangle_hit_count`
  - `segment_polygon_hitcount`
  - `point_nearest_segment`
- added packed/raw call paths for:
  - overlay
  - ray hitcount
  - segment-polygon hitcount
  - point-nearest-segment
- made `run_embree(..., result_mode="raw")` a first-class path even for ordinary record inputs by routing through `prepare_embree(...).bind(...).run_raw()`

Updated [__init__.py](/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py):

- exported `PackedTriangles`
- exported `PackedRays`
- exported `pack_triangles(...)`
- exported `pack_rays(...)`

### Tests

Added [goal18_result_mode_test.py](/Users/rl2025/rtdl_python_only/tests/goal18_result_mode_test.py):

- `run_embree(..., result_mode="raw")` rejects invalid modes
- raw result mode matches ordinary dict rows for:
  - `lsi`
  - `pip`
  - `overlay`
  - `ray_tri_hitcount`
  - `segment_polygon_hitcount`
  - `point_nearest_segment`
- prepared raw execution works for the Goal 18 extended workloads
- packed rays / packed triangles match the ordinary Embree path

Updated [goal17_prepared_runtime_test.py](/Users/rl2025/rtdl_python_only/tests/goal17_prepared_runtime_test.py):

- Goal 17’s old “overlay unsupported” assertion is removed
- replaced with an acceptance check for overlay under the new Goal 18 scope

Updated [report_smoke_test.py](/Users/rl2025/rtdl_python_only/tests/report_smoke_test.py):

- added a smoke test for the Goal 18 comparison/report generator

### Benchmark / Report

Added [goal18_compare_result_modes.py](/Users/rl2025/rtdl_python_only/scripts/goal18_compare_result_modes.py):

- measures current dict-return `run_embree(...)`
- measures first-class raw `run_embree(..., result_mode="raw")`
- measures prepared dict hot median
- measures prepared raw hot median
- includes Goal 15 native lower-bound comparisons only for `lsi` and `pip`

Generated [goal18_low_overhead_runtime_continuation_2026-04-01.md](/Users/rl2025/rtdl_python_only/docs/reports/goal18_low_overhead_runtime_continuation_2026-04-01.md)

## Measured Result

The current Goal 18 report shows:

- raw mode matches dict mode on all six current local Embree workloads
- first-class raw mode improves over the ordinary dict-return path on all six workloads
- prepared raw hot medians show materially larger gains than the ordinary dict-return path

Selected values:

### LSI

- current dict total: `0.000246792 s`
- first-class raw total: `0.000093375 s`
- prepared raw hot median: `0.000009458 s`
- raw speedup vs current dict: `2.64x`
- prepared raw speedup vs current dict: `26.09x`

### PIP

- current dict total: `0.000097708 s`
- first-class raw total: `0.000053292 s`
- prepared raw hot median: `0.000003833 s`
- raw speedup vs current dict: `1.83x`
- prepared raw speedup vs current dict: `25.49x`

### Non-native-comparison workloads

Prepared raw speedups vs current dict:

- `overlay`: `2.75x`
- `ray_tri_hitcount`: `9.03x`
- `segment_polygon_hitcount`: `15.57x`
- `point_nearest_segment`: `9.84x`

## Validation

Executed successfully:

- `PYTHONPATH=src:. python3 scripts/goal18_compare_result_modes.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal17_prepared_runtime_test tests.goal18_result_mode_test tests.report_smoke_test`
- `PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'`

Current full suite result:

- `79` tests passed

## Acceptance Claim

This implementation should satisfy the accepted Goal 18 bar:

1. DSL kernels remain unchanged
2. `run_embree(..., result_mode="raw")` is now first-class
3. prepared/raw support extends across the current local Embree workload surface
4. correctness parity is preserved by direct raw-vs-dict checks
5. native-comparison claims remain limited to `lsi` and `pip`
