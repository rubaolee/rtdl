# RTDL Architecture, API, And Performance Overview

Archived historical overview.

Date: 2026-04-05
Historical scope: this document captures a pre-`v0.4.0` milestone view centered on older `pip` and RayJoin-era performance narratives. It is preserved for architectural history, not as the current front-door release summary.

Current source of truth:

- [README.md](../README.md)
- [docs/README.md](README.md)
- [docs/release_reports/v0_4/release_statement.md](release_reports/v0_4/release_statement.md)
- [docs/release_reports/v0_4/support_matrix.md](release_reports/v0_4/support_matrix.md)


## What RTDL is

RTDL is a high-level spatial query language and runtime.

The intended user experience is:

- describe the spatial workload once at the RTDL level
- run it across multiple backends
- keep the query semantics stable
- validate results against trusted references when needed

At the current milestone, the strongest demonstrated workload family is:

- long exact-source `county_zipcode`
- positive-hit `pip`

## Execution model

At a high level, RTDL executes a spatial join as:

1. load datasets
2. convert them into RTDL logical records
3. lower the authored kernel to a backend-ready workload
4. prepare or pack backend-ready geometry when needed
5. run broad-phase candidate generation on the selected backend
6. exact-finalize candidates when the backend path requires host truth
7. emit stable RTDL result rows

For the current mature backend/workload story, this usually means:

- RTDL authorship and orchestration in Python
- native traversal and candidate generation in:
  - OptiX
  - Embree
  - Vulkan
- host exact finalization for trusted final truth on candidate subsets

## What Python does

Python owns:

- the DSL surface
- kernel compilation/lowering orchestration
- dataset ingestion
- backend dispatch
- prepared-execution caching
- row conversion at the public API boundary

Python should **not** repeatedly do hot-path bulk geometry work when the input
data is unchanged.

That is why recent performance work focused on:

- prepared execution reuse
- canonical tuple identity fast paths
- reuse of prepacked points and polygons

## What native backends do

The native backends own the heavy traversal work.

### OptiX

- primary NVIDIA high-performance backend
- mature on the accepted long exact-source `county_zipcode` positive-hit `pip`
  surface
- beats PostGIS on the accepted prepared and repeated raw-input boundaries

### Embree

- primary CPU high-performance backend
- mature on the same accepted long exact-source surface
- beats PostGIS on the accepted prepared and repeated raw-input boundaries

### Vulkan

- portable GPU backend
- hardware-validated
- parity-clean on the accepted long exact-source prepared and repeated raw-input
  boundaries
- currently slower than PostGIS, OptiX, and Embree on that surface

Strategic role:

- OptiX and Embree are the current performance backends
- Vulkan is the portable correctness-preserving backend

## Timing boundaries

The project intentionally separates timing boundaries.

### Prepared / execution-ready

What is timed:

- prepared backend execution after the geometry is already packed and bound

Why it matters:

- isolates backend execution cost more directly

### Repeated raw-input

What is timed:

- ordinary RTDL calls in one process over repeated identical raw inputs

Why it matters:

- shows what users get from runtime-owned caching without manually calling
  `prepare_*`, `pack_*`, or `bind(...)`
- reflects the current runtime-owned fast path shared by the native backends:
  - prepared-execution cache reuse
  - identity-based canonical input reuse
  - primed packed-geometry reuse when dataset views provide it

### Bounded validation

What is timed:

- smaller or partial accepted surfaces used for correctness and smoke closure

Why it matters:

- useful for backend bring-up and bounded confidence
- should not be misreported as full long-workload closure

## Current performance picture

For the accepted long exact-source `county_zipcode` positive-hit `pip` surface:

### Prepared boundary

- OptiX:
  - about `2.13-2.54 s`
- Embree:
  - about `1.04-1.44 s`
- Vulkan:
  - about `6.14 s`
- PostGIS:
  - about `3.05-3.40 s`

### Repeated raw-input boundary

- OptiX:
  - best repeated about `1.087 s`
- Embree:
  - best repeated about `1.092 s`
- Vulkan:
  - best repeated about `6.710 s`
- PostGIS:
  - about `3.09-3.58 s`

Historical honest reading at that milestone:

- OptiX and Embree were the strongest performance backends on the accepted surface under discussion
- Vulkan was complete and correct on that accepted surface, but slower

The released `v0.4.0` nearest-neighbor line has a newer backend/performance story than the one summarized here.

## API shape

Current public usage is backend-symmetric.

Typical raw-input execution:

```python
rows = rt.run_optix(kernel, points=points, polygons=polygons)
rows = rt.run_embree(kernel, points=points, polygons=polygons)
rows = rt.run_vulkan(kernel, points=points, polygons=polygons)
```

Prepared execution:

```python
prepared = rt.prepare_optix(kernel)
bound = prepared.bind(points=packed_points, polygons=packed_polygons)
rows = bound.run()
```

Equivalent prepared flows exist for Embree and Vulkan.

## Current API limitations

The current mature native `pip` paths support:

- `boundary_mode='inclusive'`

The DSL compiler still accepts other authored boundary modes, but the current
native lowering path rejects unsupported `boundary_mode` values before backend
execution. That is an explicit current contract, not silent fallback.

## Oracle position

The oracles are not current performance targets.

Accepted trust position:

- Python oracle:
  - trusted on deterministic mini envelopes
- native C oracle:
  - trusted on deterministic small envelopes

They exist for:

- quick verification
- demos
- correctness confidence

not as large-package performance paths.

## Q/A

### Are the datasets read from files on disk?

Usually yes.

Current accepted workflows commonly start from:

- ArcGIS feature-layer pages stored on disk
- converted CDB-like files
- PostGIS tables loaded from those logical records

### Does the CPU still do work after GPU traversal?

Yes, often.

For the mature positive-hit `pip` paths, the backend often does conservative
candidate generation first, and the CPU exact-finalizes only those candidates.

### Why can Python hurt performance?

Python hurts performance when it repeatedly repacks or reshapes large geometry
payloads on the hot path.

That is why recent performance work focused on:

- canonical record forms
- identity-based cache keys
- reuse of packed geometry

### Can RTDL honestly claim performance now?

Yes, but only with the right boundary.

Current honest claim:

- RTDL + OptiX beats PostGIS on the accepted long exact-source
  `county_zipcode` positive-hit `pip` surface for repeated calls
- RTDL + Embree does as well
- Vulkan does not, but it remains a real supported backend
