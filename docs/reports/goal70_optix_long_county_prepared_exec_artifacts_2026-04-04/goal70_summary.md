# Goal 70 OptiX Long County Prepared-Execution Summary

Date: `2026-04-04`
Status: `measured internal result only, do not publish`

Scope:
- long workload only
- case: `county_zipcode`
- backend: `optix`
- contract: positive-hit `pip`
- timing mode: execution-ready / prepacked (`prepare_optix` + `pack_points` + `pack_polygons` outside timed section)

Measured runs:
- run 1 artifact: `/home/lestat/work/rtdl_python_only/build/goal70_county_prepared_exec`
- run 1 OptiX: `2.642049846 s`
- run 1 PostGIS: `3.333370466 s`
- run 1 parity: `True`
- run 2 artifact: `/home/lestat/work/rtdl_python_only/build/goal70_county_prepared_exec_rerun`
- run 2 OptiX: `2.652621304 s`
- run 2 PostGIS: `3.313063422 s`
- run 2 parity: `True`

Outcome:
- best OptiX run: `2.642049846 s`
- best paired PostGIS run: `3.333370466 s`
- parity preserved across both runs: `True`
- OptiX beat PostGIS on both long-workload reruns: `True`
- row count: `39073`
- digest: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`
