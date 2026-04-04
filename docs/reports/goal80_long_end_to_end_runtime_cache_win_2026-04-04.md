# Goal 80 Report: Long End-to-End Runtime-Cache Win

Date: 2026-04-04
Status: complete

## Summary

Goal 80 asked whether RTDL could beat PostGIS on a long `county_zipcode`
positive-hit `pip` workload under an ordinary raw-input end-to-end call path,
without requiring user-visible `prepare_*`, `pack_*`, or `bind(...)` calls.

The accepted answer is yes for the OptiX repeated-call boundary.

On Linux, on the real `top4_tx_ca_ny_pa` county/zipcode package, ordinary
repeated raw-input OptiX calls now beat PostGIS after the runtime-owned cache
warms, while preserving exact parity on every rerun.

## What Changed

The key issue was that the Goal 76 identity-based prepared-execution cache
could only fast-path canonical RTDL geometry tuples, but the real CDB dataset
helpers still returned dictionaries. That meant the accepted large
county/zipcode path never used the fast path.

Goal 80 fixed that by:

- returning canonical `Point` / `Polygon` records from:
  - `/Users/rl2025/rtdl_python_only/src/rtdsl/datasets.py`
- keeping current callers compatible where they still accepted dict-shaped rows
- allowing the PostGIS loading helpers to accept canonical point/polygon
  records without re-shaping them into dictionaries:
  - `/Users/rl2025/rtdl_python_only/scripts/goal50_postgis_ground_truth.py`

Those changes activate the runtime-owned prepared cache on the real
county/zipcode top4 package rather than only on synthetic canonical tuples.

## Accepted Measurement Boundary

- host: `lestat-lx1`
- workload: `county_zipcode`
- predicate: positive-hit `pip`
- backend: `optix`
- timing boundary: ordinary repeated raw-input end-to-end calls in one process
- package:
  - county: `/home/lestat/work/rayjoin_sources/goal80_top4_package/top4_county.cdb`
  - zipcode: `/home/lestat/work/rayjoin_sources/goal80_top4_package/top4_zipcode.cdb`
- non-claim:
  - this is not a first-call cold-start win
  - this is not a prepared/prepacked manual-call win

## Measured Result

PostGIS on the same package:

- run 1: `0.374158744 s`
- run 2: `0.369906195 s`
- run 3: `0.367889968 s`

OptiX repeated raw-input end-to-end:

- first run: `1.443262336 s`
- repeated run 2: `0.146764501 s`
- repeated run 3: `0.142673727 s`

Parities:

- row count: `7863`
- SHA-256: exact match on all reruns
- `parity_preserved_all_reruns`: `true`

## Interpretation

Goal 80 does not show that the full cold OptiX raw-input path beats PostGIS.
The first raw-input call remains slower than PostGIS.

Goal 80 does show that RTDL's runtime-owned cache now closes the end-to-end gap
for long repeated raw-input calls on the real top4 county/zipcode package,
without forcing users to manually switch to prepared or packed APIs.

That is an important feasibility result for the stack:

- RTDL remains a high-level interface
- OptiX remains the fast backend
- the runtime, not the programmer, now owns the repeated-call preparation win

## Evidence

- measurement artifact:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal80_long_end_to_end_runtime_cache_win_artifacts_2026-04-04/optix/summary.json`
- measurement summary:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal80_long_end_to_end_runtime_cache_win_artifacts_2026-04-04/optix/summary.md`

## Residual Work

The remaining gap is the cold first-call path.

The most likely next optimization is:

- automatic packed-polygon reuse

That would target the still-expensive first-call preparation cost without
changing user code or weakening parity.
