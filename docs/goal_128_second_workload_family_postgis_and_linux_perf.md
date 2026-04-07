# Goal 128: Second Workload Family PostGIS And Linux Perf

Date: 2026-04-06
Status: in progress locally

## Goal

Take the newly closed `segment_polygon_anyhit_rows` family and prepare the same
external-evidence path that made `segment_polygon_hitcount` a strong feature:

- PostGIS correctness validation
- Linux large-row backend performance measurement

## Required outcomes

1. add a PostGIS validation harness for any-hit rows
2. add a Linux large-row performance harness for any-hit rows
3. add local tests for artifact rendering and dataset handling
4. state the local environment blockers honestly if the external run cannot be
   performed here

## Current status

The harness code and tests are being added locally.

The expected external-run blockers on this Mac are already visible:

- no `psql`
- no `createdb`
- no `psycopg2`
- native CPU/oracle still inherits the existing local `geos_c` linker gap

So this goal can advance the code surface locally, but the actual Linux/PostGIS
evidence must still come from a capable environment.
