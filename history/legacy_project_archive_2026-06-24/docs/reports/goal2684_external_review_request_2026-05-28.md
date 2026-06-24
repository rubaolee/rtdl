# External Review Request: Goal2684 Generic RT Hit-Stream Handoff

Please review Goal2684 for architecture boundary correctness before any
performance claim is made.

## Scope

Goal2684 adds a generic RT-produced hit stream:

```text
RAY_TRIANGLE_HIT_STREAM_3D -> rows (ray_id, primitive_id)
```

RayDB then maps `primitive_id` to app-owned group/value columns in Python and
uses Triton for generic grouped continuation.

## Files To Review

- `src/rtdsl/generic_primitives.py`
- `src/rtdsl/embree_runtime.py`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/primitive_hierarchy.py`
- `src/native/embree/rtdl_embree_prelude.h`
- `src/native/embree/rtdl_embree_scene.cpp`
- `src/native/embree/rtdl_embree_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `examples/v2_0/research_benchmarks/raydb_style/README.md`
- `scripts/goal2684_raydb_hit_stream_triton_pod_runner.py`
- `tests/goal2684_generic_rt_hit_stream_handoff_test.py`
- `docs/rtdl_primitive_catalog.md`
- `docs/reports/goal2684_generic_rt_hit_stream_handoff_2026-05-28.md`

## Questions

1. Does the native engine remain app-free? Specifically, do Embree and OptiX
   expose only generic ray/triangle hit-stream behavior without RayDB, SQL,
   table, predicate, or aggregate semantics?
2. Are the row schema and overflow semantics stable enough for a partner
   handoff contract?
3. Is the app-owned `primitive_id -> group/value` mapping placed at the correct
   boundary, or should it become a separate generic gather primitive before
   promotion?
4. Does the RayDB full path correctly separate RT traversal, hit-stream
   materialization, Triton continuation, and app row presentation?
5. Does the pod runner record enough phase timing and correctness information
   for later RT-vs-Embree and native-grouped-vs-hit-stream comparison?
6. Is there any hidden performance overclaim in docs, metadata, README text, or
   report wording?

## Known Limitation

Current local validation covers CPU and Embree behavior. OptiX/Triton pod timing
is blocked until a pod exposes working CUDA/NVML to Python and the native OptiX
library can be rebuilt and loaded. The current docs intentionally make no public
speedup claim.

## Requested Verdict

Please answer with one of:

- `Accept`
- `Accept with fixes`
- `Reject`

List blocking issues first, then non-blocking recommendations.
