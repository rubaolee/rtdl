# Goal1672 Native App-Leakage Migration Classification

Date: 2026-05-10

Status: migration planning artifact for the v1.8 / v2.0 app-agnostic engine
track.

## Verdict

The Goal1668 dirty baseline is now classified into concrete migration actions.
This classification is not an allowlist. Every listed native symbol remains blocked
for app-agnostic native-engine release claims until it is migrated to a generic
primitive/descriptor path or mechanically quarantined outside the release
surface.

Machine-readable artifact:

- `docs/reports/goal1672_native_app_leakage_migration_classification_2026-05-10.json`

Source baseline:

- `docs/reports/goal1668_native_leakage_manifest_baseline_2026-05-10.json`

## Classification Summary

| Required action | Unique symbols |
| --- | ---: |
| `replace_by_generic_packet` | 70 |
| `rename_or_replace_with_generic_columnar_descriptor` | 25 |
| `quarantine_legacy_wrapper` | 1 |

Backend distribution:

| Backend | Unique symbols |
| --- | ---: |
| Apple RT | 7 |
| Embree | 17 |
| HIPRT | 12 |
| OptiX | 32 |
| Oracle/native CPU | 15 |
| Root wrapper | 1 |
| Vulkan | 12 |

Migration-family distribution:

| Migration family | Unique symbols | Accepted direction |
| --- | ---: | --- |
| `columnar_row_filter_reduce` | 30 | generic columnar descriptors plus generic reductions |
| `generic_geometry_candidate_collection` | 29 | generic candidate packets, any-hit/count, and app-owned exact semantics |
| `bounded_nearest_candidate_collection` | 14 | generic bounded collection with app-owned nearest-neighbor interpretation |
| `frontier_edge_traversal` | 10 | generic frontier/edge packets lowered in Python |
| `generic_geometry_anyhit` | 6 | generic point/ray versus primitive any-hit packets |
| `ray_packet_preparation` | 5 | generic ray packet preparation and grouped primitive outputs |
| `app_level_distance_reduction` | 1 | generic nearest candidates plus Python/partner-owned Hausdorff reduction |
| `legacy_oracle_wrapper` | 1 | quarantine outside the release surface or remove |

## Release-Gate Meaning

This artifact converts Goal1668 from "there is leakage" into "this is the work
queue." It does not relax the v1.7/v2.0 gate:

- wrapper-backed Python APIs still fail the gate if the underlying native symbol
  remains app-shaped;
- historical/proof symbols are acceptable only if mechanically quarantined
  outside the release surface;
- performance recovery must come from generic RTDL primitive packets, generic
  reductions, partner tensor handoff, and explicit transfer paths;
- PyTorch and CuPy partner work must not add partner-specific native backdoors
  or app-shaped engine ABI fields.

## First Migration Order

Recommended order:

1. `ray_packet_preparation`: replace pose-shaped OptiX helpers with generic ray
   packet preparation and grouped any-hit/count outputs.
2. `generic_geometry_anyhit`: replace PIP-shaped entry points with generic
   point/ray versus primitive any-hit packets.
3. `bounded_nearest_candidate_collection`: replace KNN-shaped rows with generic
   bounded candidate collection plus app-owned interpretation.
4. `columnar_row_filter_reduce`: split DB dataset helpers into generic
   columnar descriptors, predicate packets, and generic reduction outputs.
5. `frontier_edge_traversal`: lower graph/BFS semantics in Python and pass only
   generic frontier/edge packets to native code.
6. Quarantine or delete the legacy oracle root wrapper before using oracle
   symbols as app-agnostic release evidence.

This order attacks the smaller, clearer app-shaped surfaces first and leaves
the broader columnar and graph migrations until the descriptor and partner
contracts are firmer.

## First Migration Result

Goal1673 completed the first local source migration for
`ray_packet_preparation`: the OptiX 2-D prepared any-hit path now uses generic
group-index/group-flag native symbols instead of pose-shaped native symbols.
See
`docs/reports/goal1673_optix_pose_to_group_native_migration_2026-05-10.md`.

Goal1674 removed the single `legacy_oracle_wrapper` item by renaming the root
oracle implementation chunk from `rtdl_oracle_polygon.cpp` to
`rtdl_oracle_geometry_cells.cpp`. This removes `rtdl_oracle_polygon` from the
strict native symbol set, but does not migrate the broader oracle polygon/GIS
API family.

Goal1681 completed the first local source migration for
`generic_geometry_anyhit`: the six `pip`-family native callables/exports
across Embree, HIPRT, OptiX, Oracle, and Vulkan were renamed to generic
point/primitive any-hit packet exports. The HIPRT internal kernel filename
hint `rtdl_hiprt_pip_2d.cu` was renamed to
`rtdl_hiprt_point_primitive_anyhit_2d.cu`. See
`docs/reports/goal1681_pip_to_point_primitive_anyhit_native_migration_2026-05-10.md`.

Goal1682 completed the first (and only) local source migration for
`app_level_distance_reduction`: the single Embree directed-Hausdorff
native export was renamed to a generic max-distance nearest-candidate
export, with Hausdorff semantics retained in the Python
`directed_hausdorff_2d_embree` helper. See
`docs/reports/goal1682_hausdorff_to_max_distance_nearest_candidate_native_migration_2026-05-10.md`.


Goal1688 completed the first local source migration for
`frontier_edge_traversal`: eight of ten `bfs`-shaped native callables/
exports across Embree, HIPRT, OptiX, Oracle, and Vulkan were renamed to
generic frontier/edge traversal packet exports. The HIPRT internal kernel
filename hint `rtdl_hiprt_bfs_expand.cu` was renamed to
`rtdl_hiprt_frontier_edge_traversal_packet.cu`. The two Apple RT BFS
discover symbols (`rtdl_apple_rt_run_bfs_discover_compute` and the
internal Metal kernel function name `rtdl_bfs_discover`) are deliberately
deferred to a later goal. See
`docs/reports/goal1688_bfs_to_frontier_edge_traversal_native_migration_2026-05-11.md`.

Goal1690 completed that Apple RT remainder by renaming the exported compute
entry point to `rtdl_apple_rt_run_frontier_discover_compute` and the embedded
Metal kernel function to `rtdl_frontier_discover`. The strict real-symbol scan
now reports zero `bfs` family symbols; the remaining release-surface work was
`db`, `polygon`, and `knn`. See
`docs/reports/goal1690_apple_rt_bfs_to_frontier_discover_native_migration_2026-05-11.md`.

Goal1695 completed the `bounded_nearest_candidate_collection` migration by
renaming the fourteen `knn`-family native ABI names across Embree, OptiX,
Oracle, and Vulkan to generic `k_closest_hits` terminology while preserving the
Python-facing `knn_rows` and `bounded_knn_rows` DSL semantics. The strict
real-symbol scan now reports zero `knn` family symbols; the remaining
release-surface work is `db` and `polygon`. See
`docs/reports/goal1695_knn_to_k_closest_hits_native_migration_2026-05-11.md`.

Goal1697 completed the polygon/shape migration by renaming the twenty-nine
`polygon`-family native ABI names across Apple RT, Embree, HIPRT, OptiX,
Oracle, and Vulkan to generic `shape`, `shape_pair`, and
`shape_set_overlap_ratio` terminology while preserving Python-facing
polygon/GIS DSL semantics. The strict real-symbol scan now reports zero
`polygon` family symbols; the remaining release-surface work is `db`. See
`docs/reports/goal1697_polygon_to_shape_native_migration_2026-05-11.md`.

Goal1699 completed the `columnar_row_filter_reduce` migration by renaming the
thirty lowercase `db`-family native ABI names across Apple RT, Embree, HIPRT,
OptiX, and Vulkan to generic columnar payload, multi-predicate scan, predicate
match, and grouped-reduction terminology while preserving Python-facing
database analytics semantics. The strict real-symbol scan now reports zero
tracked app-shaped native callable/export families; only uppercase
`RTDL_DB_*` data-kind/operator constants remain as documented regex false
positives. See
`docs/reports/goal1699_db_to_columnar_payload_native_migration_2026-05-11.md`.

## Blocked Wording

Still blocked:

```text
RTDL native internals are fully app-agnostic.
```

Allowed planning wording:

```text
RTDL has classified the current native app-shaped leakage into migration
families and required actions; every listed symbol remains excluded from
app-agnostic native-engine release claims until migrated or quarantined.
```
rts/goal1688_bfs_to_frontier_edge_traversal_native_migration_2026-05-11.md`.

## Blocked Wording

Still blocked:

```text
RTDL native internals are fully app-agnostic.
```

Allowed planning wording:

```text
RTDL has classified the current native app-shaped leakage into migration
families and required actions; every listed symbol remains excluded from
app-agnostic native-engine release claims until migrated or quarantined.
```
