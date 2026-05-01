# Goal904: OptiX Native Graph-Ray Mode Scaffold

Date: 2026-04-24

## Verdict

Implemented the first OptiX graph-ray lowering for BFS and triangle-count behind
an explicit native mode. The public default remains conservative until a real
RTX cloud gate compiles and validates this path.

## What Changed

The new native mode is selected by:

```text
RTDL_OPTIX_GRAPH_MODE=native
```

or by the app CLIs:

```text
--optix-graph-mode native
```

The default `auto` mode still uses the existing host-indexed correctness path
for OptiX BFS and triangle-count. This avoids promoting an unvalidated RTX
claim from macOS/local source edits.

## Lowering

The OptiX graph-ray path mirrors the accepted Goal903 Embree design:

- each CSR edge becomes a custom-AABB graph-edge primitive at `(src_vertex, 0)`
- `dst_vertex` is stored as primitive payload
- BFS shoots one source-column ray per frontier vertex
- triangle-count shoots one source-column ray for `u` and one for `v` per seed
- OptiX any-hit programs collect candidate outgoing edges
- CPU-side graph-state bookkeeping remains outside traversal

For BFS, the device any-hit stage handles visited filtering and optional
dedupe through GPU flags, then emits `RtdlBfsExpandRow`.

For triangle-count, the device any-hit stage emits endpoint-neighbor candidate
records. The host then intersects the two candidate lists and applies the
existing ordering/uniqueness semantics.

## Files Changed

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `examples/rtdl_graph_bfs.py`
- `examples/rtdl_graph_triangle_count.py`
- `examples/rtdl_graph_analytics_app.py`
- `tests/goal904_optix_graph_ray_mode_test.py`

## Honesty Boundary

This goal does not claim successful RTX runtime validation. It adds source-level
native OptiX graph-ray mode and exposes it explicitly for the next RTX pod run.

No public claim changes until:

- `make build-optix` passes on the RTX host
- native BFS rows match CPU/oracle rows
- native triangle-count rows match CPU/oracle rows
- phase/artifact logs prove the native graph-ray path was selected
- external review accepts the RTX artifact

## Review Remediation

Claude's first review blocked the initial source shape because the OptiX
pipeline builder sets `pipelineLaunchParamsVariableName = "params"`, while the
combined graph kernel declared separate launch-param symbols. The implementation
has been remediated by splitting the source into `kGraphBfsRayKernelSrc` and
`kGraphTriangleRayKernelSrc`, each declaring its own `__constant__ ... params`
symbol before PTX compilation. This keeps the native BFS and triangle-count
graph-ray paths independently compatible with the existing RTDL OptiX pipeline
builder.

## Verification

Local verification is source/API level because this Mac does not have the OptiX
runtime environment:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal904_optix_graph_ray_mode_test tests.goal903_embree_graph_ray_traversal_test tests.goal902_app_by_app_rt_usage_report_test -v
PYTHONPATH=src:. python3 -m py_compile examples/rtdl_graph_bfs.py examples/rtdl_graph_triangle_count.py examples/rtdl_graph_analytics_app.py tests/goal904_optix_graph_ray_mode_test.py tests/goal903_embree_graph_ray_traversal_test.py src/rtdsl/app_support_matrix.py
git diff --check
```

The next material validation requires a real RTX cloud host.
