# Goal 128 Report: Second Workload Family PostGIS And Linux Perf

Date: 2026-04-06
Status: local harness ready, external run pending

## Summary

Goal 127 made `segment_polygon_anyhit_rows` a real RTDL workload family in the
codebase. Goal 128 prepares the next closure layer:

- PostGIS-backed correctness checking
- Linux large-row backend performance reporting

## Local additions

Added:

- `src/rtdsl/goal128_segment_polygon_anyhit_postgis.py`
- `tests/goal128_segment_polygon_anyhit_postgis_test.py`

The new module provides:

- `run_postgis_segment_polygon_anyhit_rows(...)`
- `run_goal128_segment_polygon_anyhit_postgis_validation(...)`
- `run_goal128_segment_polygon_anyhit_linux_large_perf(...)`
- markdown/json artifact writers for both result families

## Local validation

The local test surface for the new workload family remains green:

- `PYTHONPATH=src:. python3 -m unittest tests.goal10_workloads_test tests.baseline_contracts_test tests.rtdsl_language_test tests.test_core_quality`
  - `105` tests
  - `OK`
  - `1` skipped

Additional Goal 128 harness tests are intended to validate:

- dataset loading for the any-hit family
- artifact writing for PostGIS-validation payloads
- artifact writing for Linux-large-perf payloads

## Current blocker

The external-evidence run cannot be completed on this Mac because the required
environment is missing:

- `psql`: unavailable
- `createdb`: unavailable
- `psycopg2`: unavailable

Also, native CPU/oracle execution on this machine still inherits the existing
local `geos_c` linker limitation.

So the current honest state is:

- the Goal 128 harness is locally implementable
- the actual Linux/PostGIS execution must happen on a capable external host

## Next execution step

Run the new Goal 128 harness on the accepted Linux/PostGIS environment and
publish:

- parity vs PostGIS on large deterministic datasets
- current and prepared backend timings on Linux
- the resulting artifact summary
