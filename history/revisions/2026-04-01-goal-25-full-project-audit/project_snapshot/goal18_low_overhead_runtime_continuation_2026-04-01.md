# Goal 18 Report: Low-Overhead Runtime Continuation

## Scope

Goal 18 continues the Goal 17 low-overhead Embree work.

This slice makes `run_embree(..., result_mode="raw")` a first-class path and extends the prepared/raw runtime across the currently supported local Embree workloads.

## Result Summary

### lsi

- dataset: `authored_lsi_minimal`
- row count: `2`
- raw matches dict: `True`
- current dict total: `0.000246792 s`
- first-class raw total: `0.000093375 s`
- prepared dict hot median: `0.000012750 s`
- prepared raw hot median: `0.000009458 s`
- raw speedup vs current dict: `2.64x`
- prepared raw speedup vs current dict: `26.09x`
- Goal 15 native lower-bound: `0.000965458 s`
- The Goal 15 native lower-bound is shown only as historical context; it is not directly comparable to this Goal 18 micro-measurement because the fixture and timing scope differ.

### pip

- dataset: `authored_pip_minimal`
- row count: `2`
- raw matches dict: `True`
- current dict total: `0.000097708 s`
- first-class raw total: `0.000053292 s`
- prepared dict hot median: `0.000005625 s`
- prepared raw hot median: `0.000003833 s`
- raw speedup vs current dict: `1.83x`
- prepared raw speedup vs current dict: `25.49x`
- Goal 15 native lower-bound: `0.000432375 s`
- The Goal 15 native lower-bound is shown only as historical context; it is not directly comparable to this Goal 18 micro-measurement because the fixture and timing scope differ.

### overlay

- dataset: `authored_overlay_minimal`
- row count: `1`
- raw matches dict: `True`
- current dict total: `0.000050834 s`
- first-class raw total: `0.000047959 s`
- prepared dict hot median: `0.000014209 s`
- prepared raw hot median: `0.000018500 s`
- raw speedup vs current dict: `1.06x`
- prepared raw speedup vs current dict: `2.75x`

### ray_tri_hitcount

- dataset: `authored_ray_tri_minimal`
- row count: `2`
- raw matches dict: `True`
- current dict total: `0.000088792 s`
- first-class raw total: `0.000055708 s`
- prepared dict hot median: `0.000011750 s`
- prepared raw hot median: `0.000009833 s`
- raw speedup vs current dict: `1.59x`
- prepared raw speedup vs current dict: `9.03x`

### segment_polygon_hitcount

- dataset: `authored_segment_polygon_minimal`
- row count: `2`
- raw matches dict: `True`
- current dict total: `0.000062292 s`
- first-class raw total: `0.000042292 s`
- prepared dict hot median: `0.000005417 s`
- prepared raw hot median: `0.000004000 s`
- raw speedup vs current dict: `1.47x`
- prepared raw speedup vs current dict: `15.57x`

### point_nearest_segment

- dataset: `authored_point_nearest_segment_minimal`
- row count: `2`
- raw matches dict: `True`
- current dict total: `0.000034042 s`
- first-class raw total: `0.000031166 s`
- prepared dict hot median: `0.000005125 s`
- prepared raw hot median: `0.000003459 s`
- raw speedup vs current dict: `1.09x`
- prepared raw speedup vs current dict: `9.84x`

## Interpretation

Goal 18 does not change the DSL surface. The gain comes from making the low-overhead data path directly available from `run_embree(...)` and from extending packed/prepared execution beyond the original Goal 17 pair.

Native-comparison numbers are only reported for `lsi` and `pip`, because those are the only workloads with the Goal 15 native C++ comparison baseline.

## Main Files

- [embree_runtime.py](/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py)
- [__init__.py](/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py)
- [goal18_compare_result_modes.py](/Users/rl2025/rtdl_python_only/scripts/goal18_compare_result_modes.py)
- [goal18_result_mode_test.py](/Users/rl2025/rtdl_python_only/tests/goal18_result_mode_test.py)
