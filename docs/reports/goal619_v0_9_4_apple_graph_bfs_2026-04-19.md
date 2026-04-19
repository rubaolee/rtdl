# Goal619: v0.9.4 Apple Graph `bfs_discover`

Date: 2026-04-19

Status: accepted with 2-AI consensus (Codex + Gemini 2.5 Flash bounded review).

## Scope

Goal619 adds bounded Apple GPU-backed support for graph `bfs_discover`.

This goal uses Apple Metal compute for CSR frontier expansion and visited filtering. CPU remains responsible for deterministic dedupe and result ordering.

This is not MPS RT traversal and not a graph database.

## Implemented Surface

Native entry point:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_apple_rt.mm`
- `rtdl_apple_rt_run_bfs_discover_compute(...)`

Python wrapper:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`
- `bfs_discover_apple_rt(graph, frontier, visited, dedupe=True)`

Public export:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`

Tests:

- `/Users/rl2025/rtdl_python_only/tests/goal619_apple_rt_graph_bfs_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal582_apple_rt_full_surface_dispatch_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal603_apple_rt_native_contract_test.py`

## Lowering

The bounded lowering is:

```text
VertexFrontier + CSRGraph + VertexSet
  -> Python CSR/frontier/visited normalization
  -> CPU frontier-degree prefix offsets
  -> Metal compute frontier expansion over CSR row_offsets/column_indices
  -> Metal compute visited filtering
  -> native compaction of fresh candidate rows
  -> CPU deterministic dedupe and sort by (level, dst_vertex, src_vertex)
```

Supported:

- CSR graph inputs
- frontier vertices with levels
- visited vertex filtering
- `dedupe=True`
- `dedupe=False`

Out of scope:

- multi-level BFS loops inside the backend
- GPU global dedupe
- GPU sorting
- MPS RT graph traversal
- graph database claims

## Support Matrix Change

`bfs_discover` is now marked:

```text
mode: native_metal_compute
native_candidate_discovery: no
cpu_refinement: dedupe_and_sorted_row_materialization
native_only: supported_for_csr_frontier_vertex_set
```

This means the edge expansion and visited filtering are Apple Metal compute backed. It does not claim MPS RT candidate discovery.

`triangle_match` remains compatibility-only until Goal620.

## Validation

Build:

```bash
make build-apple-rt
```

Result: passed.

Python syntax check:

```bash
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/apple_rt_runtime.py src/rtdsl/__init__.py tests/goal619_apple_rt_graph_bfs_test.py tests/goal582_apple_rt_full_surface_dispatch_test.py tests/goal603_apple_rt_native_contract_test.py
```

Result: passed.

Goal619 direct suite:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal619_apple_rt_graph_bfs_test -v
```

Result:

```text
Ran 6 tests in 0.012s
OK
```

Apple native coverage regression suite:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal582_apple_rt_full_surface_dispatch_test tests.goal596_apple_rt_prepared_closest_hit_test tests.goal597_apple_rt_masked_hitcount_test tests.goal598_apple_rt_masked_segment_intersection_test tests.goal603_apple_rt_native_contract_test tests.goal604_apple_rt_ray_hitcount_2d_native_test tests.goal605_apple_rt_point_neighbor_2d_native_test tests.goal606_apple_rt_point_neighbor_3d_native_test tests.goal607_apple_rt_point_in_polygon_positive_native_test tests.goal608_apple_rt_segment_polygon_native_test tests.goal609_apple_rt_point_nearest_segment_native_test tests.goal610_apple_rt_polygon_pair_native_test tests.goal611_apple_rt_overlay_compose_native_test tests.goal616_apple_rt_compute_skeleton_test tests.goal617_apple_rt_db_conjunctive_scan_test tests.goal618_apple_rt_db_grouped_aggregation_test tests.goal619_apple_rt_graph_bfs_test -v
```

Result:

```text
Ran 71 tests in 0.264s
OK
```

Coverage included:

- direct BFS helper equals CPU `bfs_expand_cpu`
- `run_apple_rt(..., native_only=True)` equals CPU reference
- `dedupe=True`
- `dedupe=False`
- empty frontier
- bounded 512-vertex stress parity
- support-matrix contract update
- `triangle_match` remains native-only rejected

## Honesty Boundary

Goal619 should be described as Apple Metal compute frontier expansion plus CPU deterministic dedupe/sort.

It should not be described as:

- Apple MPS RT graph traversal
- a graph database
- a full multi-hop BFS engine
- fully GPU-resident BFS
- a performance claim

## Codex Verdict

Accept as the implementation half of Goal619.

Reason: the implementation runs the graph expansion and visited-filter stage on Apple Metal compute, preserves CPU-oracle parity, and clearly states the CPU dedupe/sort boundary. Goal619 should be called closed only after external AI review accepts this same boundary.

## External Review

External review record:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal619_external_review_2026-04-19.md`

Gemini 2.5 Flash returned `ACCEPT` on a bounded evidence review. Goal619 is accepted only as Apple Metal compute frontier expansion/visited filtering plus CPU deterministic dedupe/sort. It does not close MPS RT graph traversal, full-GPU BFS, graph DB support, or performance claims.
