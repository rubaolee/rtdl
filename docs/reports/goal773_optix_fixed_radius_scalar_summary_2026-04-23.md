# Goal 773: OptiX Fixed-Radius Scalar Summary Optimization

Date: 2026-04-23

## Verdict

`IMPLEMENTED_PENDING_RTX_RERUN_AND_EXTERNAL_REVIEW`

Goal772 showed that the prepared fixed-radius Outlier/DBSCAN paths now run on real RTX 3090 hardware, but their profiler still returned one row per point and then performed Python postprocessing only to compute summary counts. Goal773 adds a scalar native summary path so app profilers can request only the number of query points that reached the neighbor threshold.

This is a local engineering optimization. It is not a new public RTX speedup claim until the RTX cloud pipeline is rerun and independently reviewed.

## Change

Added a new prepared OptiX fixed-radius ABI:

```text
rtdl_optix_count_prepared_fixed_radius_threshold_reached_2d
```

Added a Python method:

```python
PreparedOptixFixedRadiusCountThreshold2D.count_threshold_reached(
    query_points,
    radius=...,
    threshold=...,
)
```

Updated the Goal757 profiler with:

```text
--result-mode threshold_count
```

In this mode:

- Outlier detection uses `point_count - threshold_reached_count` as the scalar outlier count.
- DBSCAN uses `threshold_reached_count` as the scalar core-point count.
- Python postprocessing rows are not materialized.
- The native OptiX kernel copies back only a scalar count instead of a row buffer for the summary mode.

## Why This Matters

The earlier prepared fixed-radius profiler measured an important but mixed path:

1. OptiX traversal and any-hit threshold counting.
2. Native row-buffer creation and copy-back for every query point.
3. Python conversion of row structs into dictionaries.
4. Python app-level summary conversion.

For the app-level summaries currently used in the RTX manifest, steps 2-4 are avoidable. The scalar summary path keeps the RT traversal and threshold decision in native code and returns only the count the app needs.

## Files Changed

- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_core.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_workloads.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_api.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_prelude.h`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal757_optix_fixed_radius_prepared_perf.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal759_rtx_cloud_benchmark_manifest.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal762_rtx_cloud_artifact_report.py`
- `/Users/rl2025/rtdl_python_only/tests/goal757_prepared_optix_fixed_radius_count_test.py`

## Verification

Local portable verification passed:

```text
PYTHONPATH=src:. python3 -m unittest -v tests.goal757_prepared_optix_fixed_radius_count_test
Ran 11 tests in 0.003s
OK (skipped=2)
```

Manifest/report verification passed:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal762_rtx_cloud_artifact_report_test
Ran 7 tests in 1.030s
OK
```

Python compile verification passed:

```text
PYTHONPATH=src:. python3 -m py_compile \
  scripts/goal757_optix_fixed_radius_prepared_perf.py \
  scripts/goal759_rtx_cloud_benchmark_manifest.py \
  scripts/goal762_rtx_cloud_artifact_report.py \
  src/rtdsl/optix_runtime.py
```

Mechanical diff check passed:

```text
git diff --check
```

## Remaining Required Evidence

- Rebuild and rerun the OptiX backend on an RTX host before using performance numbers.
- Review the scalar-count semantics against the row-returning semantics.
- Keep the claim scoped to prepared fixed-radius summary counts, not full Outlier/DBSCAN applications.
