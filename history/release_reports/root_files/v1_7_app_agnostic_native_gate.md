# v1.7 App-Agnostic Native-Engine Gate

This is a release gate for the next architectural track after the current
Python+RTDL release surface.

## Gate Rule

RTDL must not publish the claim:

```text
RTDL native internals are fully app-agnostic.
```

until a superseding audit proves that the release-surface native engine has no
app-shaped, domain-shaped, or workload-shaped native exports.

## Required Audit

The gate audit must scan `src/native/` native export and callable surfaces for
at least these leakage terms:

- `db`
- `pip`
- `bfs`
- `robot`
- `pose`
- `polygon`
- `knn`
- `hausdorff`
- `jaccard`

The next expanded audit must also search for broader semantic leakage terms
that can encode app knowledge without using the initial directive vocabulary:

- `table`
- `column`
- `edge`
- `vertex`
- `agent`
- `trajectory`

Expanded-term false positives must be documented explicitly in the superseding
gate report; they must not be silently ignored.

The current baseline is documented in:

- [Goal1668 Native-Engine App-Agnostic Directive Response](../reports/goal1668_native_engine_app_agnostic_directive_response_2026-05-10.md)
- [Goal1603 Stable Native-Path App-Leakage Audit](../reports/goal1603_v1_6_stable_native_path_app_leakage_audit_2026-05-09.md)

The current migration classification is documented in:

- [Goal1672 Native App-Leakage Migration Classification](../reports/goal1672_native_app_leakage_migration_classification_2026-05-10.md)
- [Goal1673 OptiX Pose-To-Group Native Migration](../reports/goal1673_optix_pose_to_group_native_migration_2026-05-10.md)
- [Goal1674 Oracle Root Wrapper Quarantine](../reports/goal1674_oracle_root_wrapper_quarantine_2026-05-10.md)
- [Goal1676 Native Leakage Delta Regression](../reports/goal1676_native_leakage_delta_regression_2026-05-10.md)
- [Goal1680 Current Native App-Leakage Gap](../reports/goal1680_current_native_app_leakage_gap_2026-05-10.md)
- [Goal1681 PIP-To-Point-Primitive-Anyhit Native Migration](../reports/goal1681_pip_to_point_primitive_anyhit_native_migration_2026-05-10.md)
- [Goal1682 Hausdorff-To-Max-Distance-Nearest-Candidate Native Migration](../reports/goal1682_hausdorff_to_max_distance_nearest_candidate_native_migration_2026-05-10.md)
- [Goal1688 BFS-To-Frontier-Edge-Traversal Native Migration (Narrow Slice)](../reports/goal1688_bfs_to_frontier_edge_traversal_native_migration_2026-05-11.md)
- [Goal1690 Apple RT BFS-To-Frontier-Discover Native Migration](../reports/goal1690_apple_rt_bfs_to_frontier_discover_native_migration_2026-05-11.md)
- [Goal1695 KNN-To-K-Closest-Hits Native Migration](../reports/goal1695_knn_to_k_closest_hits_native_migration_2026-05-11.md)
- [Goal1697 Polygon-To-Shape Native Migration](../reports/goal1697_polygon_to_shape_native_migration_2026-05-11.md)
- [Goal1699 DB-To-Columnar-Payload Native Migration](../reports/goal1699_db_to_columnar_payload_native_migration_2026-05-11.md)

## Passing Condition

The gate passes only if one of these is true:

- the strict leakage audit returns zero app/domain/workload symbols for the
  release-surface native engine, or
- any remaining historical symbols are mechanically quarantined outside the
  release surface and cannot be called by public runners.

Quarantine is only an interim migration mechanism. A quarantined native
app-shaped surface must either be deleted or moved behind a non-release legacy
build path before RTDL can publish the v2.0-level claim that native internals
are fully app-agnostic.

## Failing Condition

The gate fails if public runners still depend on native symbols with app-shaped
names or semantics, including database, graph, robot/pose, polygon/GIS,
Hausdorff, Jaccard, or KNN-specific native backdoors.

Wrapper-backed Python APIs do not satisfy this gate if the underlying native
symbol remains app-shaped.

## Performance Rescue Direction

Performance regressions caused by removing native app backdoors must be solved
through:

- generic RTDL primitive packets,
- generic reductions,
- partner tensor handoff,
- true zero-copy or reduced-copy mechanisms,
- prepared generic input/output buffers.

Do not solve regressions by reintroducing app-specific C++/CUDA entry points.
 (Hausdorff), Jaccard, or KNN-specific native backdoors.

Wrapper-backed Python APIs do not satisfy this gate if the underlying native
symbol remains app-shaped.

## Performance Rescue Direction

Performance regressions caused by removing native app backdoors must be solved
through:

- generic RTDL primitive packets,
- generic reductions,
- partner tensor handoff,
- true zero-copy or reduced-copy mechanisms,
- prepared generic input/output buffers.

Do not solve regressions by reintroducing app-specific C++/CUDA entry points.
