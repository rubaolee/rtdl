# RTDL v0.9.4 Release Package

Status: released.

`v0.9.4` absorbs the untagged internal `v0.9.2` and `v0.9.3` Apple RT evidence
lines and adds Apple Metal compute/native-assisted coverage for bounded DB and
graph workloads.

## Scope

This package records the Apple RT expansion released as `v0.9.4`:

- all 18 current RTDL predicates are callable through `run_apple_rt`
- all 18 predicates have explicit native or native-assisted Apple execution
  modes in `rt.apple_rt_support_matrix()`
- Apple MPS RT covers supported geometry and nearest-neighbor slices
- Apple Metal compute covers bounded DB and graph slices
- CPU exact refinement, aggregation, uniqueness, or ordering remains disclosed
  where it is part of the current implementation

This package does not claim broad Apple speedup, Apple backend maturity
comparable to Embree, non-macOS support, or AMD/NVIDIA relevance for the Apple
backend.

## Start Here

- [Release Statement](release_statement.md)
- [Support Matrix](support_matrix.md)
- [Audit Report](audit_report.md)
- [Tag Preparation](tag_preparation.md)
- [Goal 615 Apple Graph/DB Architecture Plan](../../reports/goal615_v0_9_4_apple_graph_db_architecture_plan_2026-04-19.md)
- [Goal 616 Apple Metal Compute Skeleton](../../reports/goal616_v0_9_4_apple_metal_compute_skeleton_2026-04-19.md)
- [Goal 617 Apple DB Conjunctive Scan](../../reports/goal617_v0_9_4_apple_db_conjunctive_scan_2026-04-19.md)
- [Goal 618 Apple DB Grouped Aggregation](../../reports/goal618_v0_9_4_apple_db_grouped_aggregation_2026-04-19.md)
- [Goal 619 Apple Graph BFS](../../reports/goal619_v0_9_4_apple_graph_bfs_2026-04-19.md)
- [Goal 620 Apple Graph Triangle Match](../../reports/goal620_v0_9_4_apple_graph_triangle_match_2026-04-19.md)
- [Goal 622 Version Policy](../../reports/goal622_v0_9_4_version_policy_2026-04-19.md)
- [Goal 623 Backend Naming / Apple DB Boundary](../../reports/goal623_v0_9_4_backend_naming_and_apple_db_boundary_2026-04-19.md)
- [Goal 624 HIPRT / Apple Code Reorganization](../../reports/goal624_v0_9_4_hiprt_apple_native_code_reorganization_2026-04-19.md)
- [Goal 625 Total Test / Doc / Audit Gate](../../reports/goal625_v0_9_4_total_test_doc_audit_gate_2026-04-19.md)
- [Goal 625 External Consensus](../../reports/goal625_external_consensus_2026-04-19.md)

## Build And Test

On Apple Silicon macOS:

```bash
make build-apple-rt
PYTHONPATH=src:. python examples/rtdl_apple_rt_closest_hit.py
PYTHONPATH=src:. python -m unittest tests.goal582_apple_rt_full_surface_dispatch_test -v
PYTHONPATH=src:. python -m unittest tests.goal617_apple_rt_db_conjunctive_scan_test tests.goal618_apple_rt_db_grouped_aggregation_test tests.goal619_apple_rt_graph_bfs_test tests.goal620_apple_rt_graph_triangle_match_test -v
```

For the exact final release status, use the Goal 625 release-gate report.
