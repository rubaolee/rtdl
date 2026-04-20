# RTDL Current Main Support Matrix

Status: live support matrix for current `main` after the released `v0.9.5`
tag.

This page is intentionally separate from the
[v0.9.5 release support matrix](release_reports/v0_9_5/support_matrix.md).
The released `v0.9.5` tag is the public release boundary. Current `main`
contains post-release backend improvements from Goals650-653, so users who
build from the latest source should read this page together with the release
matrix.

## Boundary

- Current public release: `v0.9.5`.
- Current `main`: `v0.9.5` surface plus post-release native/native-assisted
  any-hit work.
- Current-main backend improvements are not retroactive claims about the
  released `v0.9.5` tag.
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
- Apple RT any-hit is not programmable shader-level Apple any-hit.
- `reduce_rows` is a deterministic Python standard-library helper over already
  emitted rows; it is not a native backend reduction.

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
- RT-core speedup from the GTX 1070 Linux evidence;
- AMD GPU validation for HIPRT;
- HIPRT CPU fallback;
- Apple MPS ray-tracing-hardware traversal for DB or graph workloads;
- programmable shader-level Apple any-hit;
- native backend acceleration for `reduce_rows`;
- retroactive native Vulkan or Apple any-hit support at the released
  `v0.9.5` tag boundary.

## Evidence

Current-main any-hit backend evidence is recorded in:

- [Goal650 Vulkan Native Early-Exit Any-Hit](reports/goal650_vulkan_native_early_exit_anyhit_2026-04-20.md)
- [Goal651 Apple RT 3D Any-Hit](reports/goal651_apple_rt_3d_anyhit_native_assisted_2026-04-20.md)
- [Goal652 Apple RT 2D Native-Assisted Any-Hit](reports/goal652_apple_rt_2d_native_anyhit_2026-04-20.md)
- [Goal653 Current-Main Linux Any-Hit Validation](reports/goal653_current_main_anyhit_linux_validation_2026-04-20.md)

For the public release boundary, use:

- [v0.9.5 Release Package](release_reports/v0_9_5/README.md)
- [v0.9.5 Support Matrix](release_reports/v0_9_5/support_matrix.md)
- [v0.9.5 Audit Report](release_reports/v0_9_5/audit_report.md)
