# RTDL Current Main Support Matrix

Status: live support matrix for the released `v0.9.6` tag and current `main`.

This page is intentionally separate from the
[v0.9.6 release support matrix](release_reports/v0_9_6/support_matrix.md).
The released `v0.9.6` tag is the current public release boundary. Users who
build from the latest source should read this page together with the release
matrix because stale local backend libraries may not contain the newest native
symbols until rebuilt.

For the machine-readable feature-by-engine contract, read
[Engine Feature Support Contract](features/engine_support_matrix.md). Every
public RTDL feature that developers can choose must be classified for every
engine as `native`, `native_assisted`, `compatibility_fallback`, or
`unsupported_explicit`; blank cells and silent CPU fallback are not allowed.

## Boundary

- Current public release: `v0.9.6`.
- Current `main`: released `v0.9.6` surface plus any later untagged local work.
- The `v0.9.6` release boundary includes the native/native-assisted any-hit work
  and prepared repeated-query visibility/count optimizations from Goals650-681.
- Backend libraries must be rebuilt from current source before current-main
  native paths are available.
- Stale backend libraries may fall back to compatibility dispatch or reject a
  shape when the required symbol is absent.
- This page is not a speedup claim.

## Any-Hit And Visibility Support

| Surface | CPU reference | Embree | OptiX | Vulkan | HIPRT | Apple RT |
| --- | --- | --- | --- | --- | --- | --- |
| `ray_triangle_any_hit` 2D | supported | native early-exit | native early-exit | native early-exit | native traversal-loop early-exit | MPS-prism native-assisted early-exit plus exact 2D acceptance |
| `ray_triangle_any_hit` 3D | supported | native early-exit | native early-exit | native early-exit | native traversal-loop early-exit | MPS RT nearest-intersection any-hit |
| `visibility_rows_cpu` | supported | not applicable | not applicable | not applicable | not applicable | not applicable |
| `visibility_rows(..., backend=...)` | supported through `backend="cpu"` | dispatches through any-hit | dispatches through any-hit | dispatches through any-hit | dispatches through any-hit | dispatches through any-hit |
| prepared repeated 2D any-hit | not applicable | use standard prepared execution / row path | prepared 2D scene plus optional prepacked rays | prepared 2D scene plus optional prepacked rays | prepared 2D scene | prepared 2D scene plus optional prepacked rays |
| prepared scalar visibility count | Python reduction over rows | row output then count | prepared/prepacked scalar count path | prepared/prepacked compact rows then count | prepared 2D any-hit rows then count | prepared 2D scene plus prepacked rays returns scalar blocked-ray count |
| `reduce_rows` | Python helper | Python helper after emitted rows | Python helper after emitted rows | Python helper after emitted rows | Python helper after emitted rows | Python helper after emitted rows |

Implementation notes:

- Embree any-hit uses `rtcOccluded1`.
- OptiX any-hit uses `optixTerminateRay()`.
- Vulkan any-hit uses Vulkan ray tracing shaders with `terminateRayEXT`.
- HIPRT any-hit uses HIPRT traversal and stops after the first accepted hit.
- Apple RT 3D any-hit uses `MPSRayIntersector` nearest-intersection existence.
- Apple RT 2D any-hit extrudes triangles into MPS-traversed prisms, uses
  per-ray primitive masks, clears a ray after the first exact accepted 2D hit,
  and emits `{ray_id, any_hit}` rows.
- The Apple RT prepared scalar visibility-count path is narrower than
  `visibility_rows`: it returns one blocked-ray count for prepacked 2D rays and
  does not materialize per-ray dictionaries. It currently uses nearest-hit
  existence over the prepared MPS prism acceleration structure, not a lower-level
  programmable any-hit shader.
- The OptiX prepared/prepacked visibility-count path is also narrower than full
  row emission: it reuses the OptiX build-side acceleration structure and can
  count prepacked 2D rays without materializing row dictionaries.
- The HIPRT prepared 2D any-hit path reuses HIPRT context, geometry, function
  table, kernel, and device-side build buffers. It is validated on the
  HIPRT/Orochi CUDA path, not on AMD GPU hardware.
- The Vulkan prepared 2D any-hit path reuses Vulkan context, pipeline,
  triangle buffer, BLAS, and TLAS. Its measured win requires prepacked rays;
  tuple-ray prepared calls alone can be slower because Python ray packing
  dominates.
- Apple RT any-hit is not programmable shader-level Apple any-hit.
- `reduce_rows` is a deterministic Python standard-library helper over already
  emitted rows; it is not a native backend reduction.

## Current-Main Prepared Performance Snapshot

These are workload-specific repeated-query measurements, not broad engine
rankings.

| Backend | Host / path | Measured path | Result |
| --- | --- | --- | --- |
| Apple RT | Apple M4 / Metal-MPS | prepared scene + prepacked 2D rays + scalar blocked-ray count | `0.00091-0.00133 s` per query for `32768` rays / `8192` triangles |
| OptiX | Linux GTX 1070 / OptiX-CUDA path | prepared scene + prepacked 2D rays + scalar count | about `0.000062-0.000075 s` versus direct around `0.00503 s` |
| HIPRT | Linux GTX 1070 / HIPRT-Orochi-CUDA path | prepared 2D any-hit rows | `0.007464495 s` versus direct `0.580084853 s` for `4096` rays / `1024` triangles |
| Vulkan | Linux GTX 1070 / Vulkan RT | prepared scene + prepacked 2D rays | `0.004496957 s` versus direct `0.008035034 s` for `4096` rays / `1024` triangles; `0.021956306 s` versus `0.028801230 s` for `32768` rays / `8192` triangles |

Allowed conclusion: prepared build-side data, prepacked probe-side data, and
reduced output contracts can make repeated visibility/count workloads much
faster. Not allowed: claiming broad speedups for DB, graph, one-shot calls, or
full emitted-row outputs from this table.

## Existing Workload Families

| Workload family | Current public position |
| --- | --- |
| Geometry | Released bounded segment/polygon, ray/triangle, closest-hit, and any-hit surfaces with backend-specific support by release matrix |
| Nearest neighbor | Released fixed-radius and KNN row surfaces; backend support remains workload- and dimensionality-specific |
| Graph | Released BFS and triangle-count surfaces; Apple DB/graph paths are Metal compute/native-assisted, not MPS ray-tracing traversal |
| DB-style analytics | Released bounded `conjunctive_scan`, `grouped_count`, and `grouped_sum`; RTDL is not a DBMS or arbitrary SQL engine |
| Apps | Released RTDL-plus-Python apps use RTDL for query/traversal kernels and Python for orchestration, reductions, and output |

## Non-Claims

Do not use current `main` to claim:

- broad speedup across all engines;
- broad speedup from prepared/prepacked visibility/count evidence;
- full emitted-row Apple RT speedup from the scalar visibility-count result;
- RT-core speedup from the GTX 1070 Linux evidence;
- AMD GPU validation for HIPRT;
- HIPRT CPU fallback;
- Apple MPS ray-tracing-hardware traversal for DB or graph workloads;
- programmable shader-level Apple any-hit;
- native backend acceleration for `reduce_rows`;
- retroactive native Vulkan or Apple any-hit support at the older released
  `v0.9.5` tag boundary.

## Evidence

Current-main any-hit backend evidence is recorded in:

- [Goal650 Vulkan Native Early-Exit Any-Hit](reports/goal650_vulkan_native_early_exit_anyhit_2026-04-20.md)
- [Goal651 Apple RT 3D Any-Hit](reports/goal651_apple_rt_3d_anyhit_native_assisted_2026-04-20.md)
- [Goal652 Apple RT 2D Native-Assisted Any-Hit](reports/goal652_apple_rt_2d_native_anyhit_2026-04-20.md)
- [Goal653 Current-Main Linux Any-Hit Validation](reports/goal653_current_main_anyhit_linux_validation_2026-04-20.md)
- [Goal667 Apple RT Visibility-Count Closure](reports/goal667_apple_rt_visibility_count_closure_2026-04-20.md)
- [Goal671 OptiX Prepared Any-Hit Count](reports/goal671_optix_prepared_anyhit_and_hiprt_boundary_2026-04-20.md)
- [Goal672 OptiX Prepacked Ray Any-Hit Count](reports/goal672_optix_prepacked_ray_anyhit_count_2026-04-20.md)
- [Goal673 OptiX Prepacked Ray Cleanup](reports/goal673_optix_prepacked_ray_cleanup_2026-04-20.md)
- [Goal674 HIPRT Prepared 2D Any-Hit](reports/goal674_hiprt_prepared_2d_anyhit_optimization_2026-04-20.md)
- [Goal675 Vulkan Prepared 2D Any-Hit + Packed Rays](reports/goal675_vulkan_prepared_2d_anyhit_packed_optimization_2026-04-20.md)

For the public release boundary, use:

- [v0.9.6 Release Package](release_reports/v0_9_6/README.md)
- [v0.9.6 Support Matrix](release_reports/v0_9_6/support_matrix.md)
- [v0.9.6 Audit Report](release_reports/v0_9_6/audit_report.md)
- [v0.9.5 Release Package](release_reports/v0_9_5/README.md)
- [v0.9.5 Support Matrix](release_reports/v0_9_5/support_matrix.md)
