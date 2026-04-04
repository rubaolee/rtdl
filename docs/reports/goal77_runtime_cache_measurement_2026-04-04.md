# Goal 77 Report: Runtime Cache End-to-End Measurement

Date: 2026-04-04

Status:
- complete
- local package ready
- not yet published

## Goal

Goal 77 measures whether Goal 76's runtime-owned prepared-execution cache reduces repeated-call end-to-end cost for repeated identical raw-input calls, without requiring programmers to manually call `prepare_*` and `bind(...)`.

## Scope

This package measures:

- workload: `county_zipcode`
- contract: positive-hit `pip`
- timing boundary: repeated raw-input calls in one process
- backends:
  - OptiX
  - Embree

Important boundary:

- this measured package uses the archived county/zipcode selected CDB slice from `goal28d_larger_run`
- it is not the earlier long prepared-execution package from Goals 70-72

## Linux Host

- host: `lestat-lx1`
- workspace: `/home/lestat/work/rtdl_goal77_run`
- database: `rtdl_postgis`

## Measured Artifacts

- `/Users/rl2025/rtdl_python_only/docs/reports/goal77_runtime_cache_measurement_artifacts_2026-04-04/optix/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal77_runtime_cache_measurement_artifacts_2026-04-04/optix/summary.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal77_runtime_cache_measurement_artifacts_2026-04-04/embree/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal77_runtime_cache_measurement_artifacts_2026-04-04/embree/summary.md`

## Results

### OptiX

- first raw-input run: `0.485947633 s`
- best repeated raw-input run: `0.000862041 s`
- repeated-run improvement observed: `true`
- parity preserved on all runs: `true`
- row count: `5`

### Embree

- first raw-input run: `2.464383211 s`
- best repeated raw-input run: `0.000774917 s`
- repeated-run improvement observed: `true`
- parity preserved on all runs: `true`
- row count: `5`

## Interpretation

Goal 77 shows that the runtime-owned prepared-execution cache is not just a code cleanup. On repeated identical raw-input calls in one process, both OptiX and Embree recover a dramatic repeated-call improvement automatically.

That is exactly the intended direction for RTDL:

- keep the authored kernel unchanged
- keep the runtime semantics unchanged
- move obvious repeated-call optimization into the runtime instead of forcing manual prepared-kernel usage

## Validation

Local validation:

- `python3 -m py_compile scripts/goal77_runtime_cache_measurement.py tests/goal77_runtime_cache_measurement_test.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal77_runtime_cache_measurement_test tests.goal76_runtime_prepared_cache_test`

Linux validation:

- `PYTHONPATH=src:. python3 tests/goal77_runtime_cache_measurement_test.py`
- Goal 77 measurement runs for:
  - `optix`
  - `embree`

## Accepted Meaning

Goal 77 establishes that the Goal 76 runtime-owned cache delivers a real repeated-call end-to-end benefit on the measured county/zipcode selected CDB slice, with exact parity preserved against PostGIS on every run.

## Non-Claims

- Goal 77 does not claim a win over PostGIS on this timing boundary
- Goal 77 does not claim the same numbers on the long prepared-execution package
- Goal 77 does not claim a Vulkan result yet
