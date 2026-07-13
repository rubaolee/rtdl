# X-HD Results

Current bounded result:

```text
tiny2d_author_gate_summary_pod.json
directed2d_asymmetric_author_gate_summary_pod.json
bounded2d_author_gate_summary_pod.json
bounded3d_author_gate_summary_pod.json
directed2d_asymmetric_rtdl_route_gate_summary.json
bounded2d_rtdl_route_gate_summary.json
bounded3d_rtdl_route_gate_summary.json
xhd_bounded_performance_matrix_2026-07-08.json
```

This is a bounded same-input author JSON gate on a deterministic tiny WKT
fixture. It compares the author `hd_exec` `HDResult` against the directed
`input1 -> input2` Hausdorff reference computed by the app-owned comparator.
The symmetric max remains in the JSON as a diagnostic field.

```text
author_hd_result = 1.0
author_comparison_reference = directed_a_to_b
author_comparison_reference_value = 1.0
abs_diff = 0.0
tolerance = 1e-9
matched = true
```

Directed-asymmetric fixture:

```text
fixture = directed2d_asymmetric
point_count_a = 2
point_count_b = 2
author_hd_result = 0.5
author_comparison_reference = directed_a_to_b
author_comparison_reference_value = 0.5
exact_reference.directed_b_to_a = 9.0
exact_reference.hausdorff = 9.0
abs_diff = 0.0
tolerance = 1e-6
matched = true
```

Second bounded fixture:

```text
fixture = bounded2d
point_count_a = 10
point_count_b = 9
author_hd_result = 2.0
author_comparison_reference = directed_a_to_b
author_comparison_reference_value = 2.0
abs_diff = 0.0
tolerance = 1e-6
matched = true
```

Third bounded 3D fixture:

```text
fixture = bounded3d
point_count_a = 9
point_count_b = 8
author_hd_result = 2.0
author_comparison_reference = directed_a_to_b
author_comparison_reference_value = 2.0
abs_diff = 0.0
tolerance = 1e-6
matched = true
```

Bounded 2D RTDL route gate:

```text
fixture = bounded2d
route = rtdl_numpy_columns_2d
point_count_a = 10
point_count_b = 9
author_hd_result = 2.0
author_comparison_reference = directed_a_to_b
author_comparison_distance = 2.0
exact_reference.hausdorff = 2.0
author_abs_diff = 0.0
tolerance = 1e-6
matched = true
```

Directed-asymmetric RTDL route gate:

```text
fixture = directed2d_asymmetric
route = rtdl_numpy_columns_2d
point_count_a = 2
point_count_b = 2
author_hd_result = 0.5
author_comparison_reference = directed_a_to_b
author_comparison_distance = 0.5
exact_reference.hausdorff = 9.0
author_abs_diff = 0.0
tolerance = 1e-6
matched = true
```

Bounded 3D RTDL route gate:

```text
fixture = bounded3d
route = rtdl_numpy_columns_3d
point_count_a = 9
point_count_b = 8
author_hd_result = 2.0
author_comparison_reference = directed_a_to_b
author_comparison_distance = 2.0
exact_reference.hausdorff = 2.0
author_abs_diff = 0.0
tolerance = 1e-6
matched = true
```

These artifacts route bounded same-input fixtures through RTDL public columnar
Hausdorff APIs. They are not performance results and do not claim equivalence to
the author's X-HD RT-core implementation strategy.

Bounded performance matrix:

```text
xhd_bounded_performance_matrix_2026-07-08.json
```

This matrix separates author `Running.AvgTime`, author process wall, and RTDL
local route phases. It deliberately reports no speedup or parity ratio because
the denominators and hardware do not align.

Boundary:

```text
full X-HD paper reproduction = not claimed
exact paper dataset reproduction = not claimed
performance claim = not claimed
representative same-source reproduction = not claimed
```

## Full-Public WaterBodies -> BlockGroups Corrected Comparison

Current corrected full-public geo result:

```text
xhd_goal5314_water_bg_corrected_comparison_summary.json
```

This summary supersedes the earlier Goal5311 default-author denominator for
paper-log comparison. Goal5311 ran author `hd_exec` with its default
`n_points_cell=15` and got:

```text
HDResult = 0.8970130085945129
```

The paper-branch WaterBodies/BG logs use:

```text
n_points_cell = 8
HDResult = 0.8964367508888245
```

Goal5313 reran author `hd_exec` on the same full-public WKT candidate with
`-n_points_cell=8` and reproduced the paper-log scalar exactly:

```text
author paper-config HDResult = 0.8964367508888245
```

The RTDL exact-witness route reports the same witness in float64:

```text
RTDL exact-witness float64 = 0.8964380566690101
same witness float32      = 0.8964367508888245
```

For this candidate, the allowed scalar comparison is therefore:

```text
author paper-config float32 value = 0.8964367508888245
RTDL exact-witness float64 value  = 0.8964380566690101
absolute difference               = 1.305780185645311e-06
declared tolerance                = 2e-6
```

Boundary:

```text
exact paper WKT files recovered = not claimed
Figure 5 fully reproduced = not claimed
performance parity = not claimed
author/RTDL identical internal precision = not claimed
```

The author executable was built on POD as `Author+BuildPatch`:

```text
xhd_author_build_patch_goal5112.diff
```

The patch is limited to build/toolchain compatibility:

- OptiX dev headers are pinned to `v7.7.0` so `optixInit()` matches the POD
  driver ABI.
- Three Thrust `transform_reduce` device lambdas are wrapped with
  `cuda::proclaim_return_type` for the CCCL version pulled by RMM.

No Hausdorff algorithm semantics are changed by this patch.

Additional artifacts:

```text
tiny2d_local_reference_summary.json
tiny2d_author_hd_exec_output_pod.json
directed2d_asymmetric_author_hd_exec_output_pod.json
bounded2d_author_hd_exec_output_pod.json
bounded3d_author_hd_exec_output_pod.json
goal5112_pod_configure_optix77.log
goal5112_pod_build_optix77.log
goal5112_local_cmake_configure.log
```

`goal5112_local_cmake_configure.log` is retained as a local-machine blocker
record (`No CUDA toolset found`), not as the current POD result.
