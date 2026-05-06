# RTDL v1.5 Release Audit Report

Status: all v1.5 release gates passed, and the `v1.5` annotated tag has been
published after explicit release authorization.

## Gate Summary

| Gate | Status | Evidence |
| --- | --- | --- |
| Primitive packet prerequisite | pass | Goal1393 stable primitive evidence and Goal1394 3-AI public wording consensus |
| Roadmap consensus | pass | Goal1397 3-AI standalone/partner roadmap consensus |
| `COLLECT_K_BOUNDED` resolution | pass by exclusion | row-returning apps excluded from v1.5, deferred to v1.5.1 |
| App migration/classification | pass | 14 included, 4 excluded |
| Same-contract correctness | pass | v1.5 correctness matrix closure |
| Same-contract benchmarks | pass | v1.5 benchmark evidence matrix |
| Support/maturity matrix | pass | v1.5 support maturity matrix |
| Release docs and public wording | pass | this v1.5 release-candidate package plus Goal1411 boundary/backend 3-AI consensus |

## Release Boundary

v1.5 is a standalone Embree+OptiX language/runtime completion release for the
supported surface. It is not a universal compute engine, not a package-install
release, and not a broad performance release. It is also not yet app-agnostic
inside the native engine implementation: app-name-free primitives exist, but
some native entry points remain workload-shaped compatibility/proof surfaces.

Allowed:

- generic traversal-plus-reduction primitive readiness;
- 14 included app contracts;
- 4 excluded app rows;
- source-tree usage with `PYTHONPATH=src:. python ...`;
- `COLLECT_K_BOUNDED` deferred to v1.5.1;
- v1.6-v2.0 reserved for partner mechanisms.
- app-agnostic native-engine cleanup as post-v1.5 work.

Not allowed:

- treating this audit document as authorization for any future release/tag action;
- moving or retagging `v1.5` without explicit release authorization;
- moving or retagging `v1.0`;
- claiming no whole-app speedup restriction;
- broad NVIDIA RTX, GPU, DB, graph, polygon, Jaccard, ANN, DBSCAN, robot, or
  Barnes-Hut speedup wording;
- claiming `COLLECT_K_BOUNDED` is stable;
- treating Vulkan, HIPRT, or Apple RT as active v1.5 targets.
- claiming the native engine has app-free internals.

## Result

The v1.5 release is complete from the gate perspective and the `v1.5` tag has
been published. Goal1411 records 3-AI acceptance of the native-engine
app-agnostic boundary and RTX pod Embree-vs-OptiX interpretation; it does not
authorize unbounded public speedup claims.
