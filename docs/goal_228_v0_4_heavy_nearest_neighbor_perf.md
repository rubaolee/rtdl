# Goal 228: Heavy v0.4 Nearest-Neighbor Performance Comparison

Date: 2026-04-10
Status: implemented

## Goal

Run a heavy Linux benchmark for the reopened `v0.4` nearest-neighbor line that:

- exercises both new workloads:
  - `fixed_radius_neighbors`
  - `knn_rows`
- compares these backends:
  - `cpu`
  - `embree`
  - `optix`
  - `vulkan`
  - `postgis`
- uses indexed PostGIS as the external comparison baseline
- uses real-world-derived point data rather than tiny authored fixtures

## Acceptance

- Linux benchmark uses a real-world point corpus derived from Natural Earth
  populated places
- each backend/workload measurement runs for a bounded heavy timed window of at
  least `10` seconds
- PostGIS uses spatial indexes rather than naive scan-only execution
- the benchmark records correctness/parity signals against PostGIS alongside
  timings
- the report includes analysis of strengths, weaknesses, and next optimization
  priorities

## Boundary

- This goal is a heavy nearest-neighbor performance and parity study, not a new
  release decision by itself.
- It does not claim exact equality between float-approx GPU distance outputs and
  PostGIS double-precision distances when the row identity matches and only the
  distance epsilon differs.
