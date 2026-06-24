# Goal 72 Report: Vulkan Long County Prepared-Execution Check

Date: 2026-04-04

Status:
- complete
- published

## Goal

Goal 72 measured the Vulkan positive-hit `pip` path on the long
`county_zipcode` workload under the same execution-ready / prepacked timing
boundary used in Goals 70 and 71. The objective was to preserve exact parity
and determine whether Vulkan could compete with indexed PostGIS on the same long
package.

## Key Finding

Vulkan remained parity-correct on both long `county_zipcode` reruns, but it did
**not** beat PostGIS under the execution-ready / prepacked timing boundary.

This is still a useful result. It shows that Vulkan can execute the same long
prepared positive-hit path correctly, but its current runtime is far behind both
PostGIS and the prepared OptiX/Embree paths on this workload.

## Measured Scope

Host:
- `lestat-lx1` (`192.168.1.20`)

Database:
- `rtdl_postgis`

Case:
- `county_zipcode`

Backend:
- `vulkan`

Contract:
- positive-hit `pip`

Timing mode:
- execution-ready / prepacked

## Preparation Costs

- `prepare_vulkan(...)`: `0.006754150 s`
- `pack_points(...)`: `0.162884293 s`
- `pack_polygons(...)`: `11.041934685 s`
- `prepared.bind(...)`: `0.000029641 s`

These costs are outside the timed execution region for Goal 72.

## Results

### Run 1

- Vulkan: `112.553943594 s`
- PostGIS: `3.117402789 s`
- parity vs PostGIS: `true`
- row count: `39073`
- digest:
  - `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

### Run 2

- Vulkan: `110.787909571 s`
- PostGIS: `3.127666747 s`
- parity vs PostGIS: `true`
- row count: `39073`
- digest:
  - `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

### Outcome

- Vulkan beat PostGIS on both reruns: `false`
- parity preserved on both reruns: `true`
- Vulkan remained slower by roughly:
  - run 1: `109.437 s`
  - run 2: `107.660 s`

## Interpretation

Goal 72 shows that correctness is no longer the main question for Vulkan on
this workload boundary. The main issue is runtime cost. Even after excluding
preparation and packing from the timed region, Vulkan remains far slower than
the indexed PostGIS query on the long `county_zipcode` case.

That means the next useful Vulkan work is not another claim package. It is a
real performance investigation of the prepared execution path itself, likely
inside the native Vulkan runtime rather than in Python-side preparation.

## Validation

Linux validation:

```bash
cd /home/lestat/work/rtdl_python_only
make build-vulkan
PYTHONPATH=src:. python3 -m unittest tests.goal71_prepared_backend_positive_hit_county_test
```

Result:
- build succeeded
- `3` tests
- `OK`

Imported measured artifacts used for this report:
- `docs/reports/goal72_vulkan_long_county_prepared_exec_artifacts_2026-04-04/summary.json`
- `docs/reports/goal72_vulkan_long_county_prepared_exec_artifacts_2026-04-04/summary.md`

## Accepted Meaning

Goal 72 establishes an honest negative result:

- workload: long `county_zipcode` positive-hit `pip`
- boundary: execution-ready / prepacked
- result: Vulkan remains slower than PostGIS
- parity: exact on two reruns

## Non-Claims

- Goal 72 does not claim that Vulkan beats PostGIS on this workload
- Goal 72 does not claim that Vulkan is close to OptiX or Embree on this long
  county case
- Goal 72 does not change the accepted full-matrix `pip` baseline
- Goal 72 does not attempt a Vulkan redesign
