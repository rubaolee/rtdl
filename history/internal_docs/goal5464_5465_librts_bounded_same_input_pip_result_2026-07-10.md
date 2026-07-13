# Goals5464-5465 LibRTS Bounded Same-Input PIP Result

Date: 2026-07-10

Status:

```text
implemented__hardware_gate_passed__external_review_pending
```

## Objective

Add the first LibRTS PIP correctness gate without creating a LibRTS-specific
RTDL primitive and without treating Ray-Multicast or Figure 12 performance as
part of this bounded result.

The gate asks one falsifiable question:

```text
When the exact same tiny polygon and point files are passed to the pinned
author AE PIP application and to RTDL OptiX, do both report four polygon-refined PIP
hits, and does RTDL emit the four expected relation rows rather than the five
MBR-only candidates?
```

## Paper And Source Audit

The official paper describes PIP as an application that indexes polygon MBRs
and then executes exact point-in-polygon refinement. Ray-Multicast is a
Range-Intersects execution/load-balancing strategy and is not a separate PIP
result semantic. These concerns therefore remain separate.

The public `RTSpatial/RTSpatial` repository does not contain the PIP app. The
reproducible source chain is pinned through the author AE:

```text
PPoPPAE                 d605fe1bd5708cbf3c457a3a9698e0cc7bcdc14b
RTSpatial submodule     7c54c181b1058c87768767998c00e225cc58666e
SpatialQueryBenchmark   9140ad997519713bb5fdceba639a357afa4609ad
```

Author source files used by the gate:

```text
SpatialQueryBenchmark/src/query/pip.cpp
SpatialQueryBenchmark/src/query/rtspatial/pip_query.cu
SpatialQueryBenchmark/src/query/rtspatial/pip_handler.h
```

The author route inserts polygon MBRs into `rtspatial::SpatialIndex` and runs
the author device `pnpoly` callback before collecting positive hits.

## Author Build Boundary

The original SpatialQueryBenchmark top-level CMake requires unrelated CGAL and
baseline dependencies. The app-owned wrapper
`goal5464_spatialquerybenchmark_pip_only_CMakeLists.txt` builds only the exact
author PIP sources and links the pinned RTSpatial install. It does not rewrite
the PIP algorithm.

The local Linux host uses CUDA 12.0 and GCC headers that expose AMX builtins
which nvcc cannot parse through Boost. The empty app-owned
`goal5464_cuda12_compat/amxtileintrin.h` shim masks those unused AMX declarations
for this PIP-only build. PIP does not use AMX. This is a disclosed build
compatibility measure, not a semantic patch.

No Embree source, build, execution, or evidence is used.

## RTDL Program

The RTDL app is a normal language program over existing generic constructs:

```python
points = rt.input("points", rt.Points, role="probe")
polygons = rt.input("polygons", rt.Polygons, role="build")
candidates = rt.traverse(points, polygons, accel="bvh")
hits = rt.refine(
    candidates,
    predicate=rt.point_in_polygon(
        exact=False,
        boundary_mode="inclusive",
        result_mode="positive_hits",
    ),
)
return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])
```

RTDL core was not modified. The author build wrapper, input parser, fixture,
comparator, provenance pins, and claim boundary remain app-owned.

## Discriminating Fixture

The fixture has three polygons and five query points. Expected exact rows are:

```text
(point 0, polygon 0)
(point 0, polygon 2)
(point 2, polygon 1)
(point 4, polygon 0)
```

Point 1 lies inside polygon 0's MBR but outside the triangle. Therefore:

```text
MBR-only candidate count = 5
polygon-refined PIP count = 4
```

An implementation that stops after MBR filtering cannot pass.

The fixture avoids boundary points. This gate does not settle cross-system
boundary-point policy.

## Linux / OptiX Gate

Environment:

```text
host     lx1
GPU      NVIDIA GeForce GTX 1070
purpose  functional correctness only
```

Result artifact:

```text
Paper-reproduction-apps/librts-paper/results/
  librts_goal5465_same_input_pip.json
```

Observed result:

| Check | Result |
|---|---:|
| Author polygon-refined result count | 4 |
| RTDL OptiX polygon-refined result count | 4 |
| RTDL exact relation rows | 4/4 matched |
| MBR-only candidates | 5 |
| RTDL RT-core accelerated | true |
| Native engine customization | false |
| Overall gate | passed |

The author output included `Query Time 0.067 ms`. This is retained as a
diagnostic field only. It is not compared to RTDL because no aligned timing
denominator, paper hardware, paper input, warmup regime, or result-materializing
boundary has been established.

## Validation

Local behavioral and contract tests:

```text
py -m unittest \
  tests.goal5464_librts_pip_contract_audit_test \
  tests.goal5465_librts_same_input_pip_gate_test

Ran 9 tests OK
```

The same focused suite also passed on Linux with the OptiX library available:

```text
Ran 9 tests OK
```

The local nearby LibRTS query regression suite passed:

```text
Ran 25 tests OK
```

The tests cover:

- exact rows versus MBR-only candidate count;
- fail-closed polygon holes and degenerate polygons;
- CLI execution;
- exact author source selection in the build wrapper;
- author output parser failure;
- count and exact-refine gate failure modes;
- provenance and claim boundaries;
- committed Linux/OptiX evidence.

## Authorized Claim

```text
On one deterministic tiny same-input fixture, the AE-pinned author LibRTS PIP
application and RTDL OptiX both report four polygon-refined PIP hits. RTDL additionally
emits all four expected relation rows, and the fixture proves exact refinement
because MBR-only filtering would produce five candidates.
```

## Not Authorized

- author PIP pair-row agreement (the author binary exposes count only);
- boundary-point semantic parity;
- robust/exact-arithmetic PIP semantics (`exact=False` is used);
- Figure 12 reproduction;
- paper PIP dataset reproduction;
- Ray-Multicast equivalence;
- author-versus-RTDL performance ratio or parity;
- full LibRTS paper reproduction;
- a LibRTS-specific or PIP-specific RTDL core primitive;
- Embree evidence.

## Next Decision

After external review, choose between:

1. obtain or construct a provenance-classified representative PIP workload and
   repeat correctness before any performance work; or
2. audit Ray-Multicast as a generic execution/load-balancing mechanism and
   define a separate feasibility gate.

Do not merge those two claims, and do not tune tiny-fixture timing.
