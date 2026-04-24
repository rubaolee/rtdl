# Goal904 Claude Review — OptiX Native Graph-Ray Mode Scaffold

Date: 2026-04-24
Reviewer: Claude Sonnet 4.6
Verdict: **BLOCK**

---

## Summary

Goal904 adds a source-level OptiX graph-ray path for BFS and triangle-count behind
`RTDL_OPTIX_GRAPH_MODE=native`, mirroring the accepted Goal903 Embree design. The
honesty boundary is correct and well-maintained throughout. However, there is one
correctness defect in the CUDA kernel that will prevent the native path from working
on any RTX host: the device-side `__constant__` symbol names do not match the
`pipelineLaunchParamsVariableName` registered with every OptiX pipeline in this
codebase.

---

## Blocker

### B-1: Launch-params variable name mismatch (`bfs_params` / `tri_params` vs `"params"`)

**Location:** `src/native/optix/rtdl_optix_core.cpp:2046-2047`,
`src/native/optix/rtdl_optix_core.cpp:509`

`build_pipeline` hardcodes:
```cpp
pco.pipelineLaunchParamsVariableName = "params";   // line 509
```

Every existing kernel PTX in the codebase accordingly declares:
```cpp
extern "C" { __constant__ <Type> params; }
```

The new graph-ray kernel (lines 2045–2048) instead declares:
```cpp
extern "C" {
__constant__ GraphBfsParams bfs_params;
__constant__ GraphTriangleParams tri_params;
}
```

There is no symbol named `"params"` in `kGraphEdgeRayKernelSrc`. When OptiX builds
the module with `pipelineLaunchParamsVariableName = "params"`, it looks for that
symbol to know where to copy the `optixLaunch` parameter buffer. With the symbol
absent, one of the following occurs depending on the OptiX version:

- `optixModuleCreate` or `optixPipelineCreate` returns an error and the pipeline
  never builds, OR
- The module builds successfully but `optixLaunch` silently does not write the
  parameter buffer, leaving `bfs_params` and `tri_params` in uninitialized constant
  memory. All pointer fields (edges, frontier, output, etc.) will be garbage, causing
  null-pointer faults or silent wrong results the first time the native path runs on
  an RTX host.

**Fix:** Split `kGraphEdgeRayKernelSrc` into two separate kernel strings (one for
BFS, one for triangle). In each, rename the `__constant__` struct variable to
`params` and adjust the corresponding `GraphBfsLaunchParams` / `GraphTriangleLaunchParams`
host-side upload accordingly. This follows the established pattern of every other
kernel in the file.

---

## Non-blocking Findings

### N-1: Float coordinate precision ceiling (~16 M vertices)

**Location:** `rtdl_optix_core.cpp` (CUDA kernel), `__raygen__graph_bfs_probe` and
`__raygen__graph_triangle_probe`

Vertex IDs are encoded as `static_cast<float>(vertex_id)` for both the ray origin
and the AABB `minX`/`maxX`. IEEE 754 single precision can represent all integers
exactly only up to 2²⁴ ≈ 16.7 M. Beyond that, distinct uint32 vertex IDs can map to
the same float. False-positive AABB hits would arrive at the anyhit program, but the
secondary check `edge.src != f.vertex_id` (comparing uint32 values, not floats)
correctly discards them, so correctness is preserved. The ceiling is the same as
Goal903 Embree and is an understood limitation of this encoding.

### N-2: Shared PTX for two pipelines

Both `g_graph_bfs` and `g_graph_triangle` compile from the same
`kGraphEdgeRayKernelSrc` string via separate `std::call_once` guards. Each pipeline
is built with the appropriate entry-point names (raygen / miss / isect / anyhit for
BFS or triangle respectively), so program groups are wired correctly. This is
functionally correct (other than the B-1 params issue above) and carries only a minor
compile-time cost: the PTX is compiled twice instead of being shared as a module.

### N-3: `os.environ` mutation in Python examples

**Location:** `examples/rtdl_graph_bfs.py:93–103`,
`examples/rtdl_graph_triangle_count.py:84–94`

The examples set `RTDL_OPTIX_GRAPH_MODE` around the `run_optix` call and restore it
in a `finally` block. This is correct in single-threaded use and appropriate for
demonstration scripts. In multi-threaded Python contexts it would be a race, but
that is not a concern for a standalone example.

### N-4: Triangle anyhit does not deduplicate candidates

`__anyhit__graph_triangle_anyhit` emits every `(seed_index, side, dst_vertex)` hit
unconditionally. Duplicate candidates for the same `(seed_index, side, dst_vertex)`
can arrive if the BVH traversal visits an AABB more than once (unusual but not
impossible with OptiX). The host-side intersection step handles this with
`std::unique` after sorting `u_neighbors` and `v_neighbors`, so duplicates are
harmless. Worth noting for reviewers expecting the GPU path to be fully deduplicated.

---

## Correctness Analysis: What Is Sound

| Area | Assessment |
|------|-----------|
| AABB construction (`src_x ± pad`, `y ± pad`, `z ± pad`) | Correct — ray at `x=f.vertex_id, dir=(0,1,0)` intersects only AABBs at that x |
| Intersection shader reports `tmin + 1e-6` | Correct — value in `[tmin, tmax]` |
| BFS: `visited_flags` check before emit | Correct |
| BFS: `atomicExch` dedupe across concurrent rays | Correct for single-step frontier |
| BFS: `output_count` atomic add + capacity guard | Correct, overflow silently truncated |
| BFS: `cuMemsetD32(d_discovered, 0, n)` per call | Correct — no stale dedupe state |
| Triangle: two rays per seed (side 0 = u, side 1 = v) | Correct |
| Triangle: host-side set-intersection of u/v candidate buckets | Correct |
| Triangle: enforce_id_ascending filter on host | Correct, matches host-indexed reference |
| `validate_graph_csr_or_throw` | Correct — validates row_offsets, column_indices |
| `output_capacity` computed from frontier degree sum | Correct, UINT32 ceiling checked |
| `GraphEdgePipeline` / `std::call_once` | Correct lazy init, no double-init race |
| `DevPtr` RAII | Correct, covers all GPU allocations in scope |

---

## Honesty Boundary Assessment

The honesty boundary is correctly upheld throughout:

- `rt_core_accelerated` is `False` in every output payload
- `optix_performance.class` is `"host_indexed_fallback"` for OptiX BFS and triangle
- `_enforce_rt_core_requirement` raises `RuntimeError` for both BFS and triangle
  OptiX paths, preventing false RT-core claims
- Default `optix_graph_mode="auto"` routes to `run_bfs_expand_optix_host_indexed`
  and `run_triangle_probe_optix_host_indexed` (safe, validated paths)
- `RTDL_OPTIX_GRAPH_MODE=native` is the only path that routes to the new code
- The analytics app's `honesty_boundary` string explicitly names that native graph-ray
  mode is gated and that only `visibility_edges` is an RT-core candidate
- Test `test_examples_expose_native_optix_graph_mode_without_rt_core_claim` verifies
  that `require_rt_core=True` raises even in native mode
- Test `test_default_optix_graph_mode_remains_conservative_until_cloud_gate` verifies
  the auto-mode default is conservative

No public claims advance as a result of this goal. The boundary is correct.

---

## Verdict: BLOCK

Block reason: **B-1** is a pre-compile correctness defect. The native OptiX graph-ray
path will not function on an RTX host in its current form. The `params` symbol mismatch
means either the OptiX pipeline build fails outright, or the kernel executes with
uninitialized launch parameters and produces wrong results or crashes.

The fix is mechanical (split kernel sources and rename the `__constant__` structs to
`params`), but it must be done before scheduling the RTX cloud validation run. All
other aspects of the scaffold — the BVH encoding, the anyHit logic, the host-side
intersection, and the honesty boundary — are sound.

---

## B-1 Remediation Re-Review — 2026-04-24

Reviewer: Claude Sonnet 4.6
Verdict: **ACCEPT**

### Checklist

| Requirement | Result |
|---|---|
| `kGraphBfsRayKernelSrc` is a separate kernel string | PASS — `rtdl_optix_core.cpp:1989` |
| `kGraphTriangleRayKernelSrc` is a separate kernel string | PASS — `rtdl_optix_core.cpp:2088` |
| BFS kernel declares `__constant__ GraphBfsParams params;` | PASS — `rtdl_optix_core.cpp:2029` |
| Triangle kernel declares `__constant__ GraphTriangleParams params;` | PASS — `rtdl_optix_core.cpp:2120` |
| Old names `bfs_params` / `tri_params` absent from core | PASS — grep confirms no occurrences |
| `pipelineLaunchParamsVariableName = "params"` unchanged | PASS — `rtdl_optix_core.cpp:509` |
| Native mode gated by `RTDL_OPTIX_GRAPH_MODE=native` in API | PASS — `rtdl_optix_api.cpp:590-608, 625-643` |
| Native mode exposed via `--optix-graph-mode native` CLI | PASS — both example CLIs |
| Default `auto` routes to host-indexed path | PASS |
| `rt_core_accelerated: False` in all payloads | PASS |
| `_enforce_rt_core_requirement` raises even in native mode | PASS |
| No premature RTX speedup claim | PASS |

B-1 is fully remediated. No new blockers introduced.
