# Goal 50 PostGIS Ground-Truth Comparison

## Objective

Install PostgreSQL/PostGIS on the Linux validation host `192.168.1.20`, load the same bounded real-data packages already used in the RTDL Linux validation track, and compare PostGIS correctness and performance against:

- the native C/C++ oracle
- the Embree backend
- the OptiX backend

## Scope

- target host: `192.168.1.20`
- database: local PostgreSQL/PostGIS on that host
- accepted real-data packages:
  - `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
  - `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`
- workloads:
  - `lsi`
  - `pip`

## Method

1. Install PostgreSQL 16, PostGIS 3, and `python3-psycopg2` on the Linux host.
2. Load the exact same bounded staged datasets already used by Goals 41 and 47.
3. Convert them with the same RTDL chain-derived semantics already used by the RTDL backends:
   - `chains_to_segments(...)`
   - `chains_to_polygons(...)`
   - `chains_to_probe_points(...)`
4. Run PostGIS joins:
   - `lsi`: segment-vs-segment `ST_Intersects`
   - `pip`: point-vs-polygon `ST_Covers` for boundary-inclusive containment
5. Compare ordered row hashes and row counts against RTDL:
   - `run_cpu(...)`
   - `run_embree(...)`
   - `run_optix(...)`
6. Report:
   - correctness parity vs PostGIS
   - PostGIS load time
   - PostGIS query time
   - RTDL backend execution time on the same packages

## Deliverables

- setup script:
  - [scripts/goal50_setup_postgis.sh](../scripts/goal50_setup_postgis.sh)
- comparison harness:
  - [scripts/goal50_postgis_ground_truth.py](../scripts/goal50_postgis_ground_truth.py)
- test:
  - [tests/goal50_postgis_ground_truth_test.py](../tests/goal50_postgis_ground_truth_test.py)
- final report:
  - [docs/reports/goal50_postgis_ground_truth_2026-04-02.md](reports/goal50_postgis_ground_truth_2026-04-02.md)

## Boundary

- this goal evaluates PostGIS on the same bounded real-data packages already accepted in the RTDL Linux track
- it does not claim full nationwide PostGIS reproduction of the RayJoin paper
- PostGIS is treated here as an industrial-standard comparison target and an additional external correctness reference
