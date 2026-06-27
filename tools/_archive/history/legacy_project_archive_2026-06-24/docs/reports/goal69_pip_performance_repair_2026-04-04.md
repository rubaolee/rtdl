# Goal 69 Report: PIP Positive-Hit Performance Repair

Date: 2026-04-04

Status:
- complete
- ready for external review
- not published yet

## Goal

Goal 69 addressed the main performance-interpretation gap identified after the
PostGIS comparison work: RTDL's accepted `pip` contract emits the full
point-by-polygon matrix, while PostGIS answers a much narrower indexed
positive-hit query. The goal was therefore not to replace the accepted
full-matrix semantics from Goal 50, but to add and validate an explicit RTDL
`positive_hits` mode for performance-oriented workloads that only need hit rows.

## What Changed

- added explicit `result_mode="positive_hits"` support for `point_in_polygon`
  and `contains`
- implemented the sparse positive-hit mode across:
  - Python reference/runtime
  - native oracle
  - Embree
  - OptiX
  - Vulkan
- preserved `result_mode="full_matrix"` as the default and accepted parity
  baseline
- added focused tests and a dedicated Goal 69 harness:
  - `scripts/goal69_pip_positive_hit_performance.py`

## Measured Final Package

Host:
- `lestat-lx1` (`192.168.1.20`)

Reference database:
- `rtdl_postgis`

Measured cases:
- `county_zipcode`
- `blockgroup_waterbodies`

Compared accelerated backends:
- `embree`
- `optix`

PostGIS mode:
- indexed GiST-assisted positive-hit join with separate load/query timing

## Results

### County/Zipcode `top4_tx_ca_ny_pa`

- load time: `39.638083649 s`
- derived sizes:
  - points: `49981`
  - polygons: `12273`
- PostGIS indexed plan: `true`
- PostGIS plan nodes:
  - `Gather Merge`
  - `Index Scan`
  - `Nested Loop`
  - `Seq Scan`
  - `Sort`
- hit rows: `39073`

Timings:
- PostGIS: `3.238477414 s`
- Embree: `12.668624839 s`
- OptiX: `15.652318004 s`

Parity:
- Embree vs PostGIS: `true`
- OptiX vs PostGIS: `true`
- shared digest:
  - `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

Interpretation:
- the new RTDL positive-hit path is now exact on the main large accepted case
- Embree is faster than OptiX on this specific positive-hit package
- PostGIS is still faster because the database is executing a narrower indexed
  in-engine join without RTDL's runtime and row-materialization overheads

### BlockGroup/WaterBodies `county2300_s10`

- load time: `0.244869326 s`
- derived sizes:
  - points: `248`
  - polygons: `287`
- PostGIS indexed plan: `true`
- PostGIS plan nodes:
  - `Index Scan`
  - `Nested Loop`
  - `Seq Scan`
  - `Sort`
- hit rows: `197`

Timings:
- PostGIS: `0.007254268 s`
- Embree: `0.070980010 s`
- OptiX: `0.069386854 s`

Parity:
- Embree vs PostGIS: `true`
- OptiX vs PostGIS: `true`
- shared digest:
  - `fe90826148ae35eefe5ecb5c9e66ad01076a847f71bbec89a5ae320e9924ca2e`

Interpretation:
- the sparse positive-hit path is exact on the smaller accepted package as well
- Embree and OptiX are effectively tied on this package
- PostGIS still retains a large advantage on the narrow indexed positive-hit
  query shape

## Validation

Focused local validation:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.rtdsl_py_test tests.goal69_pip_positive_hit_performance_test
```

Result:
- `19` tests
- `OK`

Measured artifact inputs used for this report:
- `docs/reports/goal69_final_measured_artifacts_2026-04-04/goal69_summary.json`
- `docs/reports/goal69_final_measured_artifacts_2026-04-04/goal69_summary.md`
- `docs/reports/goal69_final_measured_artifact_note_2026-04-04.md`

## Accepted Meaning

Goal 69 closes the first honest performance-repair step for RTDL `pip`:

- the project now supports an explicit positive-hit result mode for workloads
  that do not need full-matrix output
- that mode is parity-correct against indexed PostGIS positive-hit joins on the
  two accepted measured packages
- the full-matrix Goal 50 / Goal 59 contract remains unchanged and accepted

## Non-Claims

- Goal 69 does not claim that RTDL now matches PostGIS performance
- Goal 69 does not replace the accepted full-matrix `pip` semantics
- Goal 69 does not close larger OptiX or Vulkan scalability work outside the
  measured positive-hit `pip` path
