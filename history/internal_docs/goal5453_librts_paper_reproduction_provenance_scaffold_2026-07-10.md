# Goal5453 - LibRTS Paper Reproduction Provenance Scaffold

Date: 2026-07-10

## Objective

Open LibRTS as the fifth RTDL paper-reproduction app without reclassifying the
existing LibRTS-style benchmark as paper evidence and without adding an
app-specific RTDL primitive.

## Provenance

```text
paper = LibRTS: A Spatial Indexing Library by Ray Tracing
venue = PPoPP 2025
paper DOI = 10.1145/3710848.3710850
author repository = https://github.com/RTSpatial/RTSpatial
main commit = 52509e8022abeab722f5a9a89d1917e8b481defe
Zenodo v2 DOI = 10.5281/zenodo.14209767
archive = PPoPPAE-v2.tar.gz
archive MD5 = 89e589f086038f1cd3af9e3ed67da8c8
published archive size = 23.1 GB
```

## Author Contract Audit

The public author type is `SpatialIndex<coord_t, 2>`. It supports lifecycle
operations `Init`, `Insert`, `Query`, `Update`, `Delete`, and `Clear`.
The query contract covers point-contains, range-contains, and
range-intersects. The paper additionally evaluates mutability, Ray Multicast
load balancing, and PIP.

## Existing RTDL Asset Audit

RTDL already has generic, app-neutral AABB capabilities:

```text
prepare_aabb_index_2d
query_aabb_index_2d
expanded_aabb_point_membership_rows_2d
aabb_intersection_pair_rows_2d
```

The historical benchmark has CPU, OptiX, Embree, and HIPRT evidence for
different subsets. That evidence is reusable engineering context only. It does
not prove author agreement, mutation parity, Ray Multicast equivalence, paper
dataset identity, or paper performance.

Owner backend decision:

```text
Use CPU reference locally and OptiX on POD.
Do not use, build, test, compare, or report Embree anywhere in this LibRTS
paper-reproduction campaign. HIPRT is also inactive.
```

## First Bounded Gate

Goal5453 adds four tiny boxes and five query points in WKT. The local generic
RTDL CPU row route emits exactly five membership rows:

```text
(0,0), (1,0), (1,1), (2,1), (3,2)
```

This proves fixture semantics and public API wiring. It is not author evidence.

## Local Validation

```text
Goal5453 + portfolio tests: 9 OK
Goal2574 historical LibRTS benchmark tests: 7 OK after repairing its archived
report path
```

An accidental broader legacy-test import attempted to rebuild the existing
Embree library on Windows and failed at link time on unresolved `__floattidf`.
The owner subsequently excluded Embree from the entire LibRTS campaign. The
failed build is not a Goal5453 semantic result and will not be retried.

## Next Goal

Goal5454 should first use `lestat@192.168.1.20` while no POD is available, then
repeat on a CUDA/OptiX POD when one is assigned. It should build the pinned
author repository and run the same tiny WKT fixture through the author route.
The first acceptance gate is exact result-count equality. If a minimally
instrumented app-owned collector can expose pair IDs without changing query
semantics, add canonical relation equality as the stronger gate.

The local Linux GTX 1070 result is functional evidence only. It cannot become
paper-performance evidence. The first connectivity probe from the current
Codex process timed out at TCP port 22, then the host recovered and was used by
Goal5454. The transient failure did not authorize an Embree fallback.

Do not begin paper performance, mutability, or the 23.1GB AE download before
the tiny same-input author gate passes.

## Exit Label

```text
goal5453_librts_provenance_and_local_reference_complete__author_gate_pending
```
