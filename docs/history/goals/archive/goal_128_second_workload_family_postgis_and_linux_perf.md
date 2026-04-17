# Goal 128: Second Workload Family PostGIS And Linux Perf

Date: 2026-04-06
Status: accepted

## Goal

Take the newly closed `segment_polygon_anyhit_rows` family and prepare the same
external-evidence path that made `segment_polygon_hitcount` a strong feature:

- PostGIS correctness validation
- Linux large-row backend performance measurement

## Required outcomes

1. add a PostGIS validation harness for any-hit rows
2. add a Linux large-row performance harness for any-hit rows
3. add local tests for artifact rendering and dataset handling
4. run the package on the accepted Linux/PostGIS environment and publish the
   resulting artifacts

## Current status

The harness code, tests, Linux/PostGIS execution packet, and Linux result
artifacts are now published.

Local Mac limitations remain visible and are now only a local-development
constraint:

- no `psql`
- no `createdb`
- no `psycopg2`
- native CPU/oracle still inherits the existing local `geos_c` linker gap

They did not block closure because the accepted external runs were executed on
the capable Linux host.

## Final outcome

The published Goal 128 evidence now includes:

- PostGIS-backed validation on Linux for
  - `derived/br_county_subset_segment_polygon_tiled_x64`
- Linux large-scale rows through
  - `x64`
  - `x256`
  - `x512`
  - `x1024`
- parity across
  - `cpu`
  - `embree`
  - `optix`
  - `vulkan`

So `segment_polygon_anyhit_rows` now has the same style of external-evidence
surface that earlier strengthened `segment_polygon_hitcount`.
