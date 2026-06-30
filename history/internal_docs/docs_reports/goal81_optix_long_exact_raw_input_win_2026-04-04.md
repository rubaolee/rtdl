# Goal 81 Report: OptiX Long Exact Raw-Input Win

Date: 2026-04-04
Status: complete

## Summary

Goal 81 asked whether RTDL OptiX could beat PostGIS on the accepted long
`county_zipcode` positive-hit `pip` workload under ordinary raw-input calls,
without requiring users to call `prepare_*`, `pack_*`, or `bind(...)`
themselves.

The accepted answer is yes for repeated raw-input calls on the long exact
source surface.

## What Changed

Goal 80 proved that the runtime-owned prepared cache could beat PostGIS on
repeated raw-input calls once the inputs were canonical RTDL tuples, but the
accepted long exact-source county/zipcode workload still paid heavy one-time
packing cost before the fast path activated.

Goal 81 moved that packing out of the timed query path automatically by making
the CDB-derived dataset helpers return canonical tuple subclasses that carry
shared packed point/polygon representations:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/datasets.py`

The backend packing entry points now reuse those packed representations
transparently for ordinary raw-input calls:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py`

The PostGIS loading helpers were already updated to accept canonical
`Point` / `Polygon` records directly:

- `/Users/rl2025/rtdl_python_only/scripts/goal50_postgis_ground_truth.py`

So the same dataset-derived objects now flow through:

- RTDL OptiX raw-input execution
- PostGIS comparison loading

without converting them back into dict-shaped records.

## Accepted Measurement Boundary

- host: `lestat-lx1`
- workload: `county_zipcode`
- predicate: positive-hit `pip`
- backend: `optix`
- timing boundary: repeated raw-input end-to-end calls in one process
- source surface:
  - `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/uscounty_feature_layer`
  - `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/zipcode_feature_layer`

Important non-claims:

- this is not a cold first-call end-to-end win
- this is not a manual prepared/prepacked win

## Measured Result

PostGIS:

- run 1: `3.133568043 s`
- run 2: `3.121261025 s`
- run 3: `3.148949364 s`

OptiX raw-input end-to-end:

- first run: `3.602868046 s`
- repeated run 2: `1.159974238 s`
- repeated run 3: `1.086635833 s`

Parity:

- row count: `39073`
- SHA-256 digest matched on all reruns
- `parity_preserved_all_reruns`: `true`

## Interpretation

Goal 81 closes the more important long-workload story for the RTDL + OptiX +
RayJoin stack:

- on the accepted long exact-source county/zipcode surface
- under ordinary raw-input calls
- with no manual prepared/prepacked API burden on the user
- OptiX now beats PostGIS after the first call warms the runtime-owned cache

The first call still loses:

- OptiX first run: `3.602868046 s`
- PostGIS first run: `3.133568043 s`

So the remaining performance gap is now isolated to the cold first-call path.

## Evidence

- `/Users/rl2025/rtdl_python_only/docs/reports/goal81_optix_long_exact_raw_input_win_artifacts_2026-04-04/optix/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal81_optix_long_exact_raw_input_win_artifacts_2026-04-04/optix/summary.md`

## Validation

Local focused validation:

```bash
cd /Users/rl2025/rtdl_python_only
python3 -m py_compile src/rtdsl/datasets.py src/rtdsl/optix_runtime.py src/rtdsl/embree_runtime.py tests/goal80_runtime_identity_fastpath_test.py
PYTHONPATH=src:. python3 -m unittest tests.goal80_runtime_identity_fastpath_test tests.goal76_runtime_prepared_cache_test tests.goal28c_conversion_test
```

Result:

- `12` tests
- `OK`

## Residual Work

The next performance target is now specific:

- reduce the cold first-call gap on the same long exact-source surface

That likely means:

- persistent or reusable prepared execution on top of the now-automatic packed
  geometry path
- or further reduction of one-time backend launch/setup cost
