# Goal620: v0.9.4 Apple Metal Graph Triangle Match

Date: 2026-04-19

## Verdict

Status: ACCEPTED with Codex + Gemini 2.5 Flash consensus.

Goal620 adds native Apple Metal compute support for the RTDL `triangle_match`
graph workload. This moves `triangle_match` from Apple CPU-reference
compatibility dispatch to `native_metal_compute` dispatch.

## Scope

Implemented:

- Native Objective-C++/Metal function `rtdl_apple_rt_run_triangle_match_compute`.
- Python helper `triangle_match_apple_rt(graph, seeds, order="id_ascending", unique=True)`.
- `run_apple_rt(..., native_only=True)` dispatch for RTDL kernels using `rt.triangle_match`.
- Public export `rt.triangle_match_apple_rt`.
- Apple support-matrix update marking `triangle_match` as `native_metal_compute`.
- Dedicated Goal620 correctness tests.

The native kernel performs one thread per seed edge `(u, v)`. Each thread scans
`u`'s neighbor list, checks candidate `w` against `v`'s neighbor list, and emits
triangles satisfying `u < v < w`. Python materializes unique/sorted rows after
the native kernel returns.

## Honesty Boundary

This is Apple Metal compute, not Apple MPS ray-tracing traversal. It is native
Apple GPU execution for bounded CSR graph seed-neighbor intersection, but it is
not claimed as a broad graph-performance win.

The implementation supports:

- CSR graph input.
- Edge-seed input.
- `order="id_ascending"`.
- `unique=True` and `unique=False`.

Out of scope:

- Arbitrary graph storage formats.
- Multi-hop graph programs.
- GPU-side global sort/deduplication.
- Performance claims against Embree/OptiX/Vulkan/HIPRT.

## Tests

Commands run on local macOS Apple host:

```text
make build-apple-rt
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/apple_rt_runtime.py src/rtdsl/__init__.py tests/goal620_apple_rt_graph_triangle_match_test.py tests/goal582_apple_rt_full_surface_dispatch_test.py tests/goal603_apple_rt_native_contract_test.py
PYTHONPATH=src:. python3 -m unittest tests.goal620_apple_rt_graph_triangle_match_test -v
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal582_apple_rt_full_surface_dispatch_test tests.goal595_apple_rt_perf_harness_test tests.goal596_apple_rt_prepared_closest_hit_test tests.goal597_apple_rt_masked_hitcount_test tests.goal598_apple_rt_masked_segment_intersection_test tests.goal603_apple_rt_native_contract_test tests.goal604_apple_rt_ray_hitcount_2d_native_test tests.goal605_apple_rt_point_neighbor_2d_native_test tests.goal606_apple_rt_point_neighbor_3d_native_test tests.goal607_apple_rt_point_in_polygon_positive_native_test tests.goal608_apple_rt_segment_polygon_native_test tests.goal609_apple_rt_point_nearest_segment_native_test tests.goal610_apple_rt_polygon_pair_native_test tests.goal611_apple_rt_overlay_compose_native_test tests.goal616_apple_rt_compute_skeleton_test tests.goal617_apple_rt_db_conjunctive_scan_test tests.goal618_apple_rt_db_grouped_aggregation_test tests.goal619_apple_rt_graph_bfs_test tests.goal620_apple_rt_graph_triangle_match_test -v
```

Observed results:

- Goal620 dedicated suite: 6 tests OK.
- Apple backend regression suite: 79 tests OK.

An earlier broad command using stale remembered module names failed to import 14
nonexistent test modules. That was a command-selection error, not a product test
failure; rerunning the actual Apple test filenames passed.

## Files Changed

- `src/native/rtdl_apple_rt.mm`
- `src/rtdsl/apple_rt_runtime.py`
- `src/rtdsl/__init__.py`
- `tests/goal582_apple_rt_full_surface_dispatch_test.py`
- `tests/goal603_apple_rt_native_contract_test.py`
- `tests/goal620_apple_rt_graph_triangle_match_test.py`

## Codex Assessment

Goal620 is correct within its bounded contract. The implementation is native
Apple Metal compute for the candidate/intersection work and preserves RTDL's
existing CPU oracle semantics for bounded fixtures.

## External Review

Gemini 2.5 Flash reviewed the handoff/report and changed files and returned
`ACCEPT` in:

- `docs/reports/goal620_external_review_2026-04-19.md`
