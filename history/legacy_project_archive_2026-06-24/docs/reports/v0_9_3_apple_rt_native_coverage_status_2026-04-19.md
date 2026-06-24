# v0.9.3 Apple RT Native Coverage Status

Date: 2026-04-19

Status: Goals 608-612 accepted with 2-AI consensus (Codex + Gemini 2.5 Flash).

## Current Apple RT Native/Native-Assisted Rows

`apple_rt_support_matrix()` currently reports 13 native or native-assisted rows:

- `bounded_knn_rows`
- `fixed_radius_neighbors`
- `knn_rows`
- `overlay_compose`
- `point_in_polygon`
- `point_nearest_segment`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`
- `ray_triangle_closest_hit`
- `ray_triangle_hit_count`
- `segment_intersection`
- `segment_polygon_anyhit_rows`
- `segment_polygon_hitcount`

## Goals Implemented In This Work Segment

- Goal608: `segment_polygon_hitcount` and `segment_polygon_anyhit_rows`
- Goal609: `point_nearest_segment`
- Goal610: `polygon_pair_overlap_area_rows` and `polygon_set_jaccard`
- Goal611: `overlay_compose`
- Goal612: `point_in_polygon` full-matrix support

Each goal has a report and a handoff request under:

- `/Users/rl2025/rtdl_python_only/docs/reports/`
- `/Users/rl2025/rtdl_python_only/docs/handoff/`

## Current Validation

Apple-focused suite:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal611_apple_rt_overlay_compose_native_test tests.goal610_apple_rt_polygon_pair_native_test tests.goal609_apple_rt_point_nearest_segment_native_test tests.goal608_apple_rt_segment_polygon_native_test tests.goal607_apple_rt_point_in_polygon_positive_native_test tests.goal606_apple_rt_point_neighbor_3d_native_test tests.goal605_apple_rt_point_neighbor_2d_native_test tests.goal604_apple_rt_ray_hitcount_2d_native_test tests.goal603_apple_rt_native_contract_test tests.goal582_apple_rt_full_surface_dispatch_test -v
```

Result:

```text
Ran 40 tests in 0.186s
OK
```

Mechanical checks passed:

```text
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/apple_rt_runtime.py src/rtdsl/__init__.py tests/goal607_apple_rt_point_in_polygon_positive_native_test.py tests/goal582_apple_rt_full_surface_dispatch_test.py tests/goal603_apple_rt_native_contract_test.py
git diff --check
```

## Remaining Compatibility-Only Rows

Five rows remain compatibility-only:

- `bfs_discover`
- `triangle_match`
- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

## Why These Are Different

The completed v0.9.3 work decomposes geometric workloads into MPS-supported ray/triangle or point/box candidate discovery. The remaining rows are graph and database workloads. They can probably be lowered to ray-tracing encodings, but they require a separate contract for representing graph adjacency, predicate/table cells, and group keys as Apple-compatible geometric primitives.

That design must be reviewed before implementation because a naive compatibility dispatch would not satisfy the user's requirement that the workload actually execute on Apple RT/MPS hardware.

## External Review

Gemini 2.5 Flash reviewed the Goal608-612 reports and this status summary in `/Users/rl2025/rtdl_python_only/docs/reports/goal608_612_gemini_quick_review_2026-04-19.md`.

Verdict: ACCEPT.

Gemini found no technical blockers and accepted the honesty boundary that Apple MPS RT performs candidate or flag discovery while CPU refinement/materialization remains explicitly disclosed where used. This closes Goals 608-612 under the 2-AI rule.
