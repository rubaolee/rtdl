# RTDL Engine Feature Support Contract

Status: public API contract for released `v0.9.6` and later mainline work.

Every public RTDL feature that a developer can intentionally choose should have
a defined behavior on every RTDL engine. The behavior must be one of four
states:

- `native`: the engine has a direct backend implementation for the feature.
- `native_assisted`: the engine uses its native RT/compute API for candidate
  discovery or traversal, then uses bounded host-side refinement to preserve
  exact RTDL semantics.
- `compatibility_fallback`: the feature runs correctly through a documented
  compatibility path, but it is not the engine's best/native implementation and
  must not be used as an acceleration claim.
- `unsupported_explicit`: the engine rejects the feature clearly before
  execution. Silent CPU fallback is not allowed for a feature advertised as an
  RT engine feature.

The machine-readable source of truth is
`rtdsl.engine_feature_support_matrix()`.

## Public Engine Matrix

| Feature | Embree | OptiX | Vulkan | HIPRT | Apple RT |
| --- | --- | --- | --- | --- | --- |
| `line_segment_intersection_2d` | `native` | `native` | `native` | `native` | `native_assisted` |
| `point_in_polygon_2d` | `native` | `native` | `native` | `native` | `native_assisted` |
| `overlay_compose_2d` | `native` | `native` | `native` | `native` | `native_assisted` |
| `ray_triangle_hit_count_2d` | `native` | `native` | `native` | `native` | `native_assisted` |
| `ray_triangle_hit_count_3d` | `native` | `native` | `native` | `native` | `native` |
| `ray_triangle_any_hit_2d` | `native` | `native` | `native` | `native` | `native_assisted` |
| `ray_triangle_any_hit_3d` | `native` | `native` | `native` | `native` | `native` |
| `ray_triangle_closest_hit_3d` | `native` | `native` | `native` | `native` | `native` |
| `visibility_rows` | `native` | `native` | `native` | `native` | `native_assisted` |
| `prepared_scalar_visibility_count_2d` | `compatibility_fallback` | `native` | `native` | `native` | `native_assisted` |
| `fixed_radius_neighbors_2d` | `native` | `native` | `native` | `native` | `native_assisted` |
| `fixed_radius_neighbors_3d` | `native` | `native` | `native` | `native` | `native_assisted` |
| `knn_rows_2d` | `native` | `native` | `native` | `native` | `native_assisted` |
| `knn_rows_3d` | `native` | `native` | `native` | `native` | `native_assisted` |
| `bounded_db_conjunctive_scan` | `native` | `native` | `native` | `compatibility_fallback` | `native_assisted` |
| `bounded_db_grouped_count` | `native` | `native` | `native` | `compatibility_fallback` | `native_assisted` |
| `bounded_db_grouped_sum` | `native` | `native` | `native` | `compatibility_fallback` | `native_assisted` |
| `graph_bfs` | `native` | `native` | `native` | `compatibility_fallback` | `native_assisted` |
| `graph_triangle_count` | `native` | `native` | `native` | `compatibility_fallback` | `native_assisted` |
| `reduce_rows` | `compatibility_fallback` | `compatibility_fallback` | `compatibility_fallback` | `compatibility_fallback` | `compatibility_fallback` |

## Important Boundaries

- `compatibility_fallback` is correct execution, not a speedup claim.
- `native_assisted` is still real engine work, but some exact semantics are
  enforced outside the pure RT traversal API.
- Apple RT DB and graph features are not Apple MPS ray-tracing traversal; they
  are Metal compute/native-assisted paths.
- HIPRT-on-NVIDIA/Orochi evidence is not AMD GPU validation.
- `reduce_rows` is a Python standard-library helper over emitted rows, not a
  native backend reduction.
- Stale backend libraries may reject a feature or use an older compatibility
  path until rebuilt from the current source.
