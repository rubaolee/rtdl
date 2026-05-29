# Goal2684 Post-Pod External Review Request

Date: 2026-05-28

Please perform a critical review of Goal2684 after pod validation. The goal is a
generic RT hit-stream handoff for a full RT+Triton RayDB path. The review should
decide whether the implementation is architecturally acceptable and whether the
pod artifacts are enough for internal evidence. Do not authorize public speedup
wording unless the evidence and wording are explicitly sufficient.

## Files To Review

- `src/rtdsl/generic_primitives.py`
- `src/rtdsl/embree_runtime.py`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/triton_partner_continuation.py`
- `src/native/embree/rtdl_embree_prelude.h`
- `src/native/embree/rtdl_embree_scene.cpp`
- `src/native/embree/rtdl_embree_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `scripts/goal2684_raydb_hit_stream_triton_pod_runner.py`
- `tests/goal2684_generic_rt_hit_stream_handoff_test.py`
- `docs/reports/goal2684_generic_rt_hit_stream_handoff_2026-05-28.md`
- `docs/reports/goal2684_raydb_hit_stream_triton_pod_2026-05-28_small.json`
- `docs/reports/goal2684_raydb_hit_stream_triton_pod_2026-05-28_100k.json`
- `docs/reports/goal2684_claude_review_response_2026-05-28.md`

## Review Questions

1. Does `RAY_TRIANGLE_HIT_STREAM_3D` remain app-free? Native rows should expose
   only generic `(ray_id, primitive_id)` data, with no RayDB, SQL, table,
   predicate, or aggregate semantics in the engine.
2. Are fail-closed overflow semantics correct for Embree, OptiX, and the Python
   reference?
3. Does the OptiX implementation really use RT traversal through GAS and
   `optixTrace`, rather than a CUDA-only scan hidden inside the OptiX library?
4. Does the RayDB app keep predicate encoding, group mapping, value mapping, and
   result formatting outside the native engine?
5. Is the Triton continuation reached through the public partner front door, not
   through app-specific raw kernels?
6. Are the pod artifacts credible for internal evidence? Check hardware,
   backend, row counts, modes, correctness flags, median timings, and phase
   timings.
7. What claims, if any, are safe? Separate internal engineering conclusions from
   public performance wording.
8. What are the remaining blockers before promotion or public wording?

## Known Current Finding

The pod evidence shows OptiX traversal is fast and the Triton continuation is
small for the measured RayDB count/sum cases. The large `sum` path is dominated
by hit-stream materialization and app-owned mapping, so the likely next runtime
target is device-resident hit-stream handoff or typed primitive payload columns.

## Expected Verdict Format

Use one of:

- `Accept`
- `Accept with fixes`
- `Needs more evidence`
- `Reject`

Include blocking findings first, then non-blocking findings, then recommended
next work.
