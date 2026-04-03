# Goal 50 PostGIS Ground-Truth Comparison

This report will be finalized after the Linux host run completes.

## Scope

- host: `192.168.1.20`
- database: local PostgreSQL/PostGIS
- packages:
  - `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
  - `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`
- workloads:
  - `lsi`
  - `pip`

## Method

- PostGIS is loaded with the same chain-derived RTDL inputs already used by the accepted Linux validation track.
- `lsi` uses segment tables and `ST_Intersects`.
- `pip` uses probe points, polygon rings, and boundary-inclusive `ST_Covers`.
- correctness is evaluated via ordered row counts plus SHA-256 hashes against:
  - the native C oracle
  - Embree
  - OptiX

## Status

- harness implemented
- local unit test passed
- PostgreSQL/PostGIS installed on `192.168.1.20`
- final measured results pending completion of the live host run
