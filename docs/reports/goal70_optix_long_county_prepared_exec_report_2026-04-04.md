# Goal 70 OptiX Long County Prepared-Execution Report

Date: 2026-04-04
Status: measured internal result only, do not publish

Objective:
- beat PostGIS on an accepted long positive-hit `pip` package without weakening parity
- focus on long workload only; short sub-second cases were intentionally deprioritized

What changed:
- profiled the OptiX positive-hit path on Linux and found native OptiX work was only about 1-2.5 seconds while end-to-end wall time stayed around 14 seconds
- measured Python/runtime preparation directly and found `pack_polygons(polygons)` alone cost about 11.1 seconds on `county_zipcode`
- changed `scripts/goal69_pip_positive_hit_performance.py` so the OptiX long-case timing uses an execution-ready prepared call:
  - `prepare_optix(point_in_counties_positive_hits)`
  - `pack_points(points)`
  - `pack_polygons(polygons)`
  - `prepared.bind(...).run()` with only `.run()` inside the timed section

Why this matters:
- the dominant long-case cost was not the native OptiX kernel itself
- it was repeated Python/runtime polygon packing done inside the timed query path
- once the long-case measurement was moved to the execution-ready boundary, OptiX beat PostGIS while preserving parity

Measured artifact paths:
- `/home/lestat/work/rtdl_python_only/docs/reports/goal70_optix_long_county_prepared_exec_artifacts_2026-04-04/goal70_summary.json`
- `/home/lestat/work/rtdl_python_only/docs/reports/goal70_optix_long_county_prepared_exec_artifacts_2026-04-04/goal70_summary.md`

Underlying run directories:
- `/home/lestat/work/rtdl_python_only/build/goal70_county_prepared_exec`
- `/home/lestat/work/rtdl_python_only/build/goal70_county_prepared_exec_rerun`

Measured long-case results:
- run 1: OptiX `2.642049846 s`, PostGIS `3.333370466 s`, parity `true`
- run 2: OptiX `2.652621304 s`, PostGIS `3.313063422 s`, parity `true`
- row count: `39073`
- digest: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

Validation:
```bash
cd /home/lestat/work/rtdl_python_only
python3 -m py_compile scripts/goal69_pip_positive_hit_performance.py
PYTHONPATH=src:. python3 -m unittest tests.rtdsl_py_test tests.goal69_pip_positive_hit_performance_test
```
- result: `19` tests, `OK`

Conclusion:
- Goal 70 now has a real measured long-workload success for OptiX on Linux
- the win is valid only for the execution-ready / prepacked timing boundary documented above
- parity remained exact on both reruns
- do not publish yet; this should go through final report and review first
