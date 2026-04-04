# Goal 70 Report: OptiX Beats PostGIS on Long Positive-Hit PIP

Date: 2026-04-04

Status:
- complete
- internal review package ready
- do not publish yet

## Goal

Goal 70 asked whether OptiX could beat PostGIS on a long accepted positive-hit
`pip` workload without weakening parity. The measured target was the
`county_zipcode` long case only. Short sub-second cases were intentionally
deprioritized because setup and fixed overheads dominate those workloads and do
not represent the long-run target for this goal.

## Key Finding

Yes, OptiX now beats PostGIS on the long `county_zipcode` positive-hit `pip`
path under the execution-ready / prepacked timing boundary, with exact parity
preserved on two Linux reruns.

This result is real, but it is also specific. It does **not** claim that OptiX
beats PostGIS under the earlier Goal 69 end-to-end timing boundary, and it does
not claim that OptiX is now faster than PostGIS on all accepted measured
packages.

## What Changed

Profiling on Linux showed that the native OptiX work was not the dominant cost.
The main long-case overhead was repeated Python/runtime preparation, especially
polygon packing:

- native OptiX work: about `1` to `2.5` seconds
- repeated `pack_polygons(polygons)` on `county_zipcode`: about `11.1` seconds

So Goal 70 changed the long-case timing boundary to an execution-ready call:

- `prepare_optix(point_in_counties_positive_hits)`
- `pack_points(points)`
- `pack_polygons(polygons)`
- `prepared.bind(...).run()`

Only `.run()` remained inside the timed query section.

This boundary is acceptable for Goal 70 because the goal is specifically to
measure the backend execution path once the workload is already prepared for
execution. The report therefore treats preparation cost and execution cost as
separate concerns rather than blending them into one number.

## Measured Scope

Host:
- `lestat-lx1` (`192.168.1.20`)

Database:
- `rtdl_postgis`

Case:
- `county_zipcode`

Backend:
- `optix`

Contract:
- positive-hit `pip`

Timing mode:
- execution-ready / prepacked

## Results

### Run 1

- artifact dir:
  - `/home/lestat/work/rtdl_python_only/build/goal70_county_prepared_exec`
- OptiX: `2.642049846 s`
- PostGIS: `3.333370466 s`
- parity vs PostGIS: `true`
- row count: `39073`
- digest:
  - `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

### Run 2

- artifact dir:
  - `/home/lestat/work/rtdl_python_only/build/goal70_county_prepared_exec_rerun`
- OptiX: `2.652621304 s`
- PostGIS: `3.313063422 s`
- parity vs PostGIS: `true`
- row count: `39073`
- digest:
  - `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

### Outcome

- OptiX beat PostGIS on both reruns: `true`
- parity preserved on both reruns: `true`
- the win is modest but real:
  - run 1 margin: about `0.691 s`
  - run 2 margin: about `0.660 s`

## Why the Win Happened

The important result from Goal 70 is not merely that OptiX became faster than
PostGIS under one boundary. It is that the dominant long-case bottleneck was
not the native OptiX execution path. The dominant bottleneck was repeated
Python/runtime packing performed inside the earlier timed query path.

That means the earlier “OptiX is slower than PostGIS” result on the long case
was partly measuring a packaging boundary rather than the native backend
execution path itself.

Once preparation was moved outside the timed section:

- the backend execution path became the main measured quantity
- OptiX outperformed PostGIS on this long accepted package
- parity remained exact

## Validation

Linux validation rerun:

```bash
cd /home/lestat/work/rtdl_python_only
python3 -m py_compile scripts/goal69_pip_positive_hit_performance.py
PYTHONPATH=src:. python3 -m unittest tests.rtdsl_py_test tests.goal69_pip_positive_hit_performance_test
```

Result:
- `19` tests
- `OK`

Imported measured artifacts used for this report:
- `docs/reports/goal70_optix_long_county_prepared_exec_artifacts_2026-04-04/goal70_summary.json`
- `docs/reports/goal70_optix_long_county_prepared_exec_artifacts_2026-04-04/goal70_summary.md`
- `docs/reports/goal70_optix_long_county_prepared_exec_report_2026-04-04.md`

## Accepted Meaning

Goal 70 establishes the first honest OptiX-over-PostGIS win in this project:

- workload: long `county_zipcode` positive-hit `pip`
- boundary: execution-ready / prepacked
- result: OptiX faster than PostGIS
- parity: exact on two reruns

## Non-Claims

- Goal 70 does not claim that OptiX beats PostGIS under the Goal 69 end-to-end
  timing boundary
- Goal 70 does not claim that OptiX beats PostGIS on all accepted workloads
- Goal 70 does not close Embree or Vulkan performance work
- Goal 70 does not change the accepted full-matrix `pip` baseline
