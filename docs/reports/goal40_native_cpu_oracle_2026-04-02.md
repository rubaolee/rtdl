# Goal 40 Native CPU Oracle

Date: 2026-04-02

## What Changed

A new standalone native oracle was added in:

- [rtdl_oracle.cpp](/Users/rl2025/rtdl_python_only/src/native/rtdl_oracle.cpp)

with a Python runtime wrapper in:

- [oracle_runtime.py](/Users/rl2025/rtdl_python_only/src/rtdsl/oracle_runtime.py)

`run_cpu(...)` now routes through that native oracle, while the old Python path remains available as:

- [run_cpu_python_reference](/Users/rl2025/rtdl_python_only/src/rtdsl/runtime.py)

The native oracle mirrors the old `reference.py` semantics for:

- `segment_intersection`
- `point_in_polygon`
- `overlay_compose`
- `ray_triangle_hit_count`
- `segment_polygon_hitcount`
- `point_nearest_segment`

## Semantic Rule

The native oracle is intended to preserve the old simulator behavior, not invent a new reference model.

That means it intentionally keeps:

- double-precision numeric behavior
- the current inclusive boundary rule for point-in-polygon
- the current overlay composition logic based on first-vertex containment checks
- the same point-nearest-segment tie-break rule
- the same row ordering expected by existing tests

## Verification

The following test sets passed after the switch:

- `tests.rtdsl_simulator_test`
- `tests.goal40_native_oracle_test`
- `tests.goal31_lsi_gap_closure_test`
- `tests.rtdsl_embree_test`
- `tests.goal10_workloads_test`

## Performance Observation

The first slice shows two different behaviors.

### Output-light case

For a selective `lsi` case with `2000 x 2000` segments and `0` output rows:

- native oracle median: about `0.001952 s`
- old Python reference median: about `0.936911 s`

This is a large improvement and confirms that the native oracle removes the Python nested-loop bottleneck for sparse-result oracle checks.

### Output-heavy case

For a dense `500 x 500` grid case with `250000` output rows:

- native oracle median: about `0.213499 s`
- old Python reference median: about `0.189318 s`

This means the default dict-return `run_cpu(...)` path is still dominated by Python-side row materialization when the result set is very large.

## Honest Conclusion

Goal 40 first slice successfully replaces the Python simulator core with a native oracle and keeps semantic parity.

However, the first slice does **not** mean that every `run_cpu(...)` case is now faster than Python. The current performance boundary is:

- much faster on sparse-result oracle workloads
- still limited by Python dict materialization on very row-heavy workloads

So the next CPU-oracle optimization slice, if needed later, should focus on:

- prepared inputs
- raw row views
- and lower-overhead result materialization

instead of changing the correctness model.
