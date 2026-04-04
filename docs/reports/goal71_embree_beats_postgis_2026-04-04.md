# Goal 71 Report: Embree Beats PostGIS on Long Positive-Hit PIP

Date: 2026-04-04

Status:
- complete
- internal review package ready
- do not publish yet

## Goal

Goal 71 asked whether Embree could beat PostGIS on a long accepted positive-hit
`pip` workload without weakening parity. The measured target was the long
`county_zipcode` case only. Short sub-second cases were intentionally
deprioritized because they are dominated by fixed setup costs rather than the
steady prepared execution path.

## Key Finding

Yes. Embree beats PostGIS on the long `county_zipcode` positive-hit `pip` path
under the execution-ready / prepacked timing boundary, with exact parity
preserved on two Linux reruns.

This result is specific. It does **not** claim that Embree beats PostGIS under
the Goal 69 end-to-end timing boundary, and it does **not** claim that Embree
is now faster than PostGIS on all accepted measured packages.

## What Changed

Goal 71 reused the prepared execution boundary established in Goal 70 and
applied it to Embree:

- `prepare_embree(point_in_counties_positive_hits)`
- `pack_points(points)`
- `pack_polygons(polygons)`
- `prepared.bind(...).run()`

Only `.run()` remained inside the timed query section. Preparation cost and
execution cost are therefore reported separately.

## Measured Scope

Host:
- `lestat-lx1` (`192.168.1.20`)

Database:
- `rtdl_postgis`

Case:
- `county_zipcode`

Backend:
- `embree`

Contract:
- positive-hit `pip`

Timing mode:
- execution-ready / prepacked

## Preparation Costs

- `prepare_embree(...)`: `0.045654697 s`
- `pack_points(...)`: `0.162488782 s`
- `pack_polygons(...)`: `11.025372127 s`
- `prepared.bind(...)`: `0.000021329 s`

These numbers are outside the timed execution region for Goal 71. The query
comparison below measures only the prepared `.run()` call against the indexed
PostGIS query.

## Results

### Run 1

- Embree: `1.347775829 s`
- PostGIS: `3.203224316 s`
- parity vs PostGIS: `true`
- row count: `39073`
- digest:
  - `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

### Run 2

- Embree: `1.026593471 s`
- PostGIS: `3.148009729 s`
- parity vs PostGIS: `true`
- row count: `39073`
- digest:
  - `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

### Outcome

- Embree beat PostGIS on both reruns: `true`
- parity preserved on both reruns: `true`
- the win is clear:
  - run 1 margin: about `1.855 s`
  - run 2 margin: about `2.121 s`

## Why the Win Happened

The same structural lesson from Goal 70 holds here: the long-case bottleneck is
not the core prepared execution path once the workload is already packed and
bound. On this boundary, Embree's prepared positive-hit execution is materially
faster than the indexed PostGIS query while preserving exact parity.

This does not erase the preparation cost. It means that, under a steady-state
prepared execution model, Embree is faster on this long accepted package.

## Validation

Linux validation:

```bash
cd /home/lestat/work/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal71_prepared_backend_positive_hit_county_test
```

Result:
- `3` tests
- `OK`

Imported measured artifacts used for this report:
- `docs/reports/goal71_embree_long_county_prepared_exec_artifacts_2026-04-04/summary.json`
- `docs/reports/goal71_embree_long_county_prepared_exec_artifacts_2026-04-04/summary.md`

## Accepted Meaning

Goal 71 establishes the first honest Embree-over-PostGIS win in this project:

- workload: long `county_zipcode` positive-hit `pip`
- boundary: execution-ready / prepacked
- result: Embree faster than PostGIS
- parity: exact on two reruns

## Non-Claims

- Goal 71 does not claim that Embree beats PostGIS under the Goal 69 end-to-end
  timing boundary
- Goal 71 does not claim that Embree beats PostGIS on all accepted workloads
- Goal 71 does not close Vulkan performance work
- Goal 71 does not change the accepted full-matrix `pip` baseline
