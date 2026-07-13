# RTDL v2.14.4 Source-Tree Release

Status: reviewed API consolidation and paper-app portfolio snapshot.

RTDL v2.14.4 formalizes generic capabilities that were developed and tested
under paper-app pressure. It is a source-tree release marker, not a package,
PyPI, broad performance, or full-paper-reproduction promise.

## Public System Surface

- `DeviceColumnBuffer` for format-neutral column ownership and handoff;
- `PreparedGeometrySession` for explicit prepare/query lifecycle management;
- bounded `device_order_by` / CUDA lexicographic ordering contracts;
- explicit public Numba partner continuation;
- existing CPU, Embree, and OptiX paths under their documented support gates.

`device_group_by` remains internal because its fully device-resident reduction
contract has not yet passed the public readiness gate.

## Paper-App Portfolio

Five applications pressure-test the generic language/runtime while retaining
their paper-specific semantics in `Paper-reproduction-apps/`:

- RayJoin: bounded section reproduction and prepared writer-free binary route;
- RT-BarnesHut: bounded prepared-state aggregate-hierarchy reproduction;
- RT-DBSCAN: bounded component-partition and core-flag agreement;
- X-HD: same-input directed HDResult agreement and generic nearest pipeline;
- LibRTS: scoped correctness and generic AABB/mutation system extraction.

These are scoped evidence packages. They do not collectively establish full
paper, all-dataset, all-figure, author-algorithm, or performance parity.

## Verification

- v2.14.4 API release preflight: `ready_for_public_release_staging`;
- source-tree doctor: pass, with optional native/partner warnings only;
- final LibRTS regression: 208 tests passed, 5 local OptiX-runtime skips;
- all five paper-app lines have externally reviewed bounded closeouts.

## Claim Boundary

This release does not claim broad speedup, true zero-copy for every pipeline,
automatic partner selection, public `device_group_by`, author performance
parity, full reproduction of every cited paper, or package-distribution support.
Performance statements remain tied to their exact workload, hardware, phase,
runtime regime, and reviewed artifact.
