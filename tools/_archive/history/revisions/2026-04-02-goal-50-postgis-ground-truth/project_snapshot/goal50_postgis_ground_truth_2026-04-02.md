# Goal 50 PostGIS Ground-Truth Comparison

## Result

Goal 50 completed successfully on `192.168.1.20`.

For both accepted real-data packages:

- PostGIS used indexed GiST-assisted query plans
- the native C oracle matched PostGIS exactly
- Embree matched PostGIS exactly
- OptiX matched PostGIS exactly

That means the current accepted RTDL results for these Goal 50 packages have no correctness differences from PostGIS.

## Scope

- host: `192.168.1.20`
- database: local PostgreSQL/PostGIS
- packages:
  - `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
  - `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`
- workloads:
  - `lsi`
  - `pip`
- compared RTDL backends:
  - C oracle
  - Embree
  - OptiX

## Method

- PostGIS was loaded with the same chain-derived RTDL inputs already used by the accepted Linux validation track.
- `lsi` used segment tables with GiST-index-assisted `geom &&` bbox pruning followed by RTDL-matching exact segment math.
- `pip` used probe points, polygon rings, and an index-assisted positive-hit query via `geom &&` plus boundary-inclusive `ST_Covers`.
- PostGIS positive hits were expanded into the same RTDL full-matrix `contains=0/1` truth rows before hash comparison.
- correctness was evaluated via exact row counts and SHA-256 hashes against:
  - the native C oracle
  - Embree
  - OptiX

## Corrections During The Goal

Two real RTDL `pip` issues were found and fixed before final parity was achieved:

- degenerate repeated-closing edges could incorrectly classify outside points as boundary hits
- the endpoint-range tolerance for very short edges was too loose

The remaining boundary/topology gap was then closed by switching the accepted `pip` refine path to GEOS-backed prepared-polygon `covers(point)` semantics for:

- the native C oracle
- Embree
- OptiX host-side refine

This was necessary to satisfy the strict Goal 50 rule that accepted RTDL results may not differ from PostGIS.

## Measured Results

### County ⊲⊳ Zipcode `top4_tx_ca_ny_pa`

- load time: `86.199871356 s`
- PostGIS mode: `indexed GiST-assisted joins with separate load/query timing`

`lsi`

- PostGIS: `34.032305237 s`, rows `107513`, hash `5f2a6455c95afb7c3c46d3e9f63b7384f56b41ca5bac9dc002c5b25a90aa8172`
- C oracle: parity `true`, `89.336466250 s`
- Embree: parity `true`, `80.270740817 s`
- OptiX: parity `true`, `53.290038755 s`
- PostGIS plan:
  - `uses_index = true`
  - index names: `county_zipcode_left_segments_geom_idx`
  - node types: `Gather Merge`, `Index Scan`, `Nested Loop`, `Seq Scan`, `Sort`

`pip`

- PostGIS: `0.430007831 s`, full-matrix rows `16352128`, positive hits `7817`, hash `ba09aeeccfb76d4d635a38c8e4de39813131e0931fa9bb607fab07ad15288d43`
- C oracle: parity `true`, `24.416985234 s`
- Embree: parity `true`, `16.812840088 s`
- OptiX: parity `true`, `19.255055544 s`
- PostGIS plan:
  - `uses_index = true`
  - index names: `county_zipcode_points_geom_idx`
  - node types: `Index Scan`, `Nested Loop`, `Seq Scan`, `Sort`

### BlockGroup ⊲⊳ WaterBodies `county2300_s10`

- load time: `1.001984315 s`
- PostGIS mode: `indexed GiST-assisted joins with separate load/query timing`

`lsi`

- PostGIS: `0.231961607 s`, rows `216`, hash `52028604b4e768229327d92070a8ffca506bb28676151164d6dc9f8c0905247f`
- C oracle: parity `true`, `0.228627974 s`
- Embree: parity `true`, `0.222838373 s`
- OptiX: parity `true`, `0.893340557 s`
- PostGIS plan:
  - `uses_index = true`
  - index names: `blockgroup_waterbodies_right_segments_geom_idx`
  - node types: `Index Scan`, `Nested Loop`, `Seq Scan`, `Sort`

`pip`

- PostGIS: `0.008412973 s`, full-matrix rows `71176`, positive hits `197`, hash `7d4ea3b099c5f1295391b341b45a7723baf0453dae155bb30b121fe0b95bdbef`
- C oracle: parity `true`, `0.149648431 s`
- Embree: parity `true`, `0.117168097 s`
- OptiX: parity `true`, `0.647711122 s`
- PostGIS plan:
  - `uses_index = true`
  - index names: `blockgroup_waterbodies_polygons_geom_idx`
  - node types: `Index Scan`, `Nested Loop`, `Seq Scan`, `Sort`

## Interpretation

- Goal 50 succeeded as an external industrial-standard correctness check, not just an internal cross-backend comparison.
- On the accepted packages, RTDL now matches PostGIS exactly for both `lsi` and `pip`.
- PostGIS is extremely fast on the indexed positive-hit `pip` query itself, but RTDL and PostGIS are not executing identical end-to-end work:
  - RTDL emits the full point x polygon matrix
  - the PostGIS query is an indexed positive-hit join, then expanded into RTDL-equivalent truth for parity
- OptiX is not uniformly faster than Embree or the C oracle on these bounded packages; the current OptiX path still includes host-side exact refine, which reduces GPU advantage on smaller workloads.

## Boundary

- this goal validates PostGIS against the same bounded real-data packages already accepted in the RTDL Linux track
- it does not claim full nationwide PostGIS reproduction of the RayJoin paper
- it establishes PostGIS as an external accepted correctness reference for the tested packages
