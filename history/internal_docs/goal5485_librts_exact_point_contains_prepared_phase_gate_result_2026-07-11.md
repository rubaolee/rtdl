# Goal5485: LibRTS Exact Point-Contains Prepared-Phase Gate

Date: 2026-07-11

Status: `implemented__contract_test_passed__POD_dtl_cnty_probe_matched`

## Objective

Create the next measurement boundary after the Goal5484 denominator audit.
The author Figure-6 log reports internal Query Time after index loading. The
RTDL measurement must therefore separate WKT loading, index preparation, and
prepared-index query instead of dividing author Query Time by an all-in-one
RTDL route wall.

## Implementation

The app-owned gate uses existing generic RTDL APIs:

```python
prepared = rt.prepare_aabb_index_2d(boxes, backend="optix")
payload = prepared.count(point_queries=points, operation="point_contains")
prepared.close()
```

It records:

```text
load_wkt_sec
prepare_index_sec
prepared_query_wall_sec
primitive_query_sec
```

The author side records its internal Query Time and Loading Time separately.
The gate marks the prepared-query phase as a **comparison candidate**, not as an
authorized performance ratio. It requests no relation rows and adds no
LibRTS-specific RTDL primitive.

## Local verification

The focused contract test passes and verifies that:

- prepare and prepared query are measured separately;
- the one-shot `query_aabb_index_2d` helper is not used;
- the prepared handle is closed;
- the performance ratio remains closed.

## POD status

The replacement endpoint `157.157.221.29:25039` passes the wrapper preflight
with an RTX 4000 Ada, CUDA 12.8, and a healthy OptiX SDK v8.0.0 checkout. The
RTDL OptiX library was rebuilt with explicit `sm_89`, and a tiny prepared
`point_contains` call returned count `1` with `rt_core_accelerated=true`.

The endpoint started with an empty workspace. The official 23,062,425,365-byte
archive was downloaded and its published MD5
`89e589f086038f1cd3af9e3ed67da8c8` was verified. The exact `dtl_cnty` geometry
and 100K query members were selected from that archive and independently
verified by size and SHA-256. The pinned author `query` binary was built with
the PPoPPAE/RTSpatial/SpatialQueryBenchmark commits; Ubuntu 24.04 required an
isolated GEOS 3.11 build for the author's C++ API.

The live probe passed on the RTX 4000 Ada POD. Both implementations consumed
the same files and returned `136475` point-contains results:

```text
author internal Query Time       0.0688 ms
author Loading Time              0.3854 ms (diagnostic, excluded by author metric)
RTDL WKT load                    28.5173 s
RTDL index preparation            1.1200 s
RTDL prepared query wall          0.3763 s
RTDL native primitive query       0.2162 s
```

The prepared-query value is a phase-boundary measurement candidate only. It is
not compared as a ratio to the author's internal Query Time: the implementations
use different execution models, and the author query metric is not the RTDL
prepared-query wall. No paper-performance claim is made.

## Claim boundary

Authorized:

- a generic prepared-index phase measurement contract;
- exact-input count agreement if the POD probe matches;
- separate author Query Time, RTDL prepare, and RTDL prepared-query fields.
- a live POD exact-input count match for the prepared-phase gate.

Not authorized:

- a performance ratio;
- Figure-6 reproduction;
- full-paper reproduction;
- pointwise relation equality for the count-only author output;
- Embree comparison.

The result artifact is
`Paper-reproduction-apps/librts-paper/results/librts_goal5485_dtl_cnty_prepared_phase.json`.
