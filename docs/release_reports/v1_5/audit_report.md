# RTDL v1.5 Release-Candidate Audit Report

Status: all v1.5 release-candidate gates pass; explicit release/tag action still
required.

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
| Release docs and public wording | pass | this v1.5 release-candidate package |

## Release Boundary

v1.5 is a standalone Embree+OptiX language/runtime completion candidate for the
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

- claiming a tag exists before explicit release/tag action;
- moving or retagging `v1.0`;
- claiming no whole-app speedup restriction;
- broad NVIDIA RTX, GPU, DB, graph, polygon, Jaccard, ANN, DBSCAN, robot, or
  Barnes-Hut speedup wording;
- claiming `COLLECT_K_BOUNDED` is stable;
- treating Vulkan, HIPRT, or Apple RT as active v1.5 targets.
- claiming the native engine has app-free internals.

## Result

The v1.5 release candidate is complete from the gate perspective. The next step
is an explicit release decision and tag operation if the user approves.
