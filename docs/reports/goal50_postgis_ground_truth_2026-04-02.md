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
- `lsi` uses segment tables with index-assisted `geom &&` bbox pruning followed by RTDL-matching exact segment math.
- `pip` uses probe points, polygon rings, and an index-assisted positive-hit query via `geom &&` plus boundary-inclusive `ST_Covers`.
- correctness is evaluated via ordered row counts plus SHA-256 hashes against:
  - the native C oracle
  - Embree
  - OptiX

## Status

- harness implemented
- local unit test passed
- PostgreSQL/PostGIS installed on `192.168.1.20`
- one older remote PostGIS run was rejected and terminated because its live `lsi` SQL did not use the required `geom &&` GiST-index-assisted predicate
- final measured results remain pending a rerun under the accepted indexed-ground-truth policy
