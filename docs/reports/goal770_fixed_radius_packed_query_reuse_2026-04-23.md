# Goal 770: Fixed-Radius Packed Query Reuse

Date: 2026-04-23

## Purpose

The prepared fixed-radius Outlier and DBSCAN profilers are part of the next RTX cloud batch. Before using pod time, Goal 770 removes a local Python/interface inefficiency: repeated packing of the same query points during every warm prepared OptiX iteration.

## Change

Updated:

```text
/Users/rl2025/rtdl_python_only/scripts/goal757_optix_fixed_radius_prepared_perf.py
```

The profiler now:

- packs the tiled point set once with `rt.pack_points(...)`;
- builds the prepared OptiX fixed-radius scene from the packed points;
- reuses the same packed query points in every warm iteration;
- reports `prepared_optix_pack_points_sec` separately.

Updated:

```text
/Users/rl2025/rtdl_python_only/scripts/goal762_rtx_cloud_artifact_report.py
```

The artifact report now extracts and displays the fixed-radius pack/input phase so the next RTX report can distinguish native traversal time from Python packing time.

## Verification

Focused local verification:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal757_prepared_optix_fixed_radius_count_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal761_rtx_cloud_run_all_test \
  tests.goal762_rtx_cloud_artifact_report_test \
  tests.goal763_rtx_cloud_bootstrap_check_test \
  tests.goal769_rtx_pod_one_shot_test

Ran 21 tests in 0.700s
OK (skipped=2)
```

Additional checks:

```text
python3 -m py_compile scripts/goal757_optix_fixed_radius_prepared_perf.py scripts/goal762_rtx_cloud_artifact_report.py
git diff --check
```

Both passed.

## Boundary

This is an interface cleanup and phase-reporting improvement. It should reduce repeated Python packing overhead in the next cloud run, but it is not a new RTX speedup claim until the pod rebuilds and reruns the benchmark batch.
