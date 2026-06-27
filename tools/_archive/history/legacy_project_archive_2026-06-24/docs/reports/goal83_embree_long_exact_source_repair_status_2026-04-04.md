# Goal 83 Status: Embree Long Exact-Source Repair

Current state: closed locally and ready for final review/publish.

## Initial exact-source measurement

Using a clean Linux clone at `209db71` and the exact-source directories:

- `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/uscounty_feature_layer`
- `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/zipcode_feature_layer`

The first repeated raw-input measurement using `goal77_runtime_cache_measurement.py`
for backend `embree` produced a real failure:

- PostGIS row count: `39073`
- Embree row count: `39215`
- parity vs PostGIS: `false` on every rerun
- PostGIS: about `3.10`-`3.33 s`
- Embree: about `44.99`-`47.74 s`

This is not publishable as an Embree performance win.

## Diagnosis

The bug is in the native Embree positive-hit `pip` path in
`src/native/rtdl_embree.cpp`.

Before the fix attempt:

- Embree user-geometry traversal was used to identify polygons.
- The callback directly trusted local `point_in_polygon(...)` as final truth.
- The positive-hit branch emitted rows immediately from that local check.

That differs from the stronger OptiX shape, where backend traversal is treated as
candidate generation and exact finalize remains explicit.

## Current repair direction

The local patch changes the Embree positive-hit callback path so that:

- the callback records candidate polygon primitive indices only
- rows are emitted only after exact finalize on those candidates
- GEOS `covers(...)` is used when available
- the local `point_in_polygon(...)` fallback remains only for non-GEOS builds

This should remove the stable exact-source parity drift.

## Validation state

Local focused tests after the patch:

- `tests.rtdsl_embree_test`
- `tests.goal80_runtime_identity_fastpath_test`
- `tests.goal76_runtime_prepared_cache_test`
- `tests.goal69_pip_positive_hit_performance_test`

Result:

- local Mac: `OK` with one expected Embree skip due local GEOS link state
- clean Linux clone: `19` tests, `OK`

## Final exact-source Linux result

After replacing the earlier callback-local truth path with conservative candidate
generation plus host exact finalize, the exact-source Linux reruns are now
parity-clean.

Accepted artifacts:

- prepared exact-source:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal83_embree_long_exact_source_repair_artifacts_2026-04-04/prepared/summary.json`
- repeated raw-input exact-source:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal83_embree_long_exact_source_repair_artifacts_2026-04-04/raw/summary.json`

Prepared exact-source:

- Embree: `1.773865199 s`
- PostGIS: `3.402695205 s`
- parity: `true`

Repeated raw-input exact-source:

- first run Embree: `1.959970190 s`
- repeated Embree: `1.092190547 s`
- PostGIS comparison runs:
  - `3.583030458 s`
  - `3.188612651 s`
- parity: `true` on all runs

## Current conclusion

Goal 83 succeeded.

Embree now has a clean exact-source long `county_zipcode` positive-hit `pip`
story on Linux:

- prepared exact-source win against PostGIS
- repeated raw-input exact-source win against PostGIS
- exact parity preserved
