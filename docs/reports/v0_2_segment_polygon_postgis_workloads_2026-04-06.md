# RTDL v0.2 Segment/Polygon PostGIS Workloads

Date: 2026-04-06
Status: accepted reference note

Main SQL artifact:

- [v0_2_segment_polygon_postgis_workloads.sql](/Users/rl2025/rtdl_python_only/docs/sql/v0_2_segment_polygon_postgis_workloads.sql)

## What this file is

This note explains the exact PostGIS workload path used by the current RTDL
v0.2 segment/polygon validation flow.

It covers:

- dataset handling
- raw table shape
- geometry-table construction
- indexes
- queries

The two workload families covered are:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`

## Dataset handling

The PostGIS path does not invent independent geometry.

It uses the same RTDL representative datasets that the runtime backends use.

Dataset loading entry point:

- [baseline_runner.py](/Users/rl2025/rtdl_python_only/src/rtdsl/baseline_runner.py)

Representative cases for the segment/polygon families are built from:

- authored minimal case
- fixture-backed county subset
- derived tiled county subset

### Authored minimal

Source:

- [rtdl_goal10_reference.py](/Users/rl2025/rtdl_python_only/examples/rtdl_goal10_reference.py)

This is the small hand-authored example with:

- `2` segments
- `2` polygons

### Fixture-backed county subset

Source fixture:

- `tests/fixtures/rayjoin/br_county_subset.cdb`

Builder:

- [make_fixture_segment_polygon_case](/Users/rl2025/rtdl_python_only/examples/rtdl_goal10_reference.py)

Current shape:

- first `10` segment records derived from county chains
- first `2` polygon chains with at least `3` points

### Derived tiled county subset

Dataset naming helper:

- [segment_polygon_large_dataset_name](/Users/rl2025/rtdl_python_only/src/rtdsl/goal114_segment_polygon_postgis.py)

Names look like:

- `derived/br_county_subset_segment_polygon_tiled_x64`
- `derived/br_county_subset_segment_polygon_tiled_x256`
- `derived/br_county_subset_segment_polygon_tiled_x4096`

Construction rule:

- load the fixture-backed county subset
- tile the segments and polygons `N` times
- use deterministic offsets:
  - `step_x = 30.0`
  - `step_y = 20.0`

So the tiled datasets are not random.
They are deterministic geometric copies of the same county-derived base slice.

## Raw tables

The Python harness creates and fills two raw tables.

For segments:

```sql
CREATE TABLE rtdl_v0_2_postgis.segments_raw (
    id BIGINT,
    x0 DOUBLE PRECISION,
    y0 DOUBLE PRECISION,
    x1 DOUBLE PRECISION,
    y1 DOUBLE PRECISION
);
```

For polygons:

```sql
CREATE TABLE rtdl_v0_2_postgis.polygons_raw (
    id BIGINT,
    wkt TEXT
);
```

The harness then bulk-loads those raw tables with `COPY FROM STDIN`.

Important detail:

- polygons are loaded as WKT text
- each polygon WKT is built by closing the ring if needed

## Geometry table construction

After raw loading, the validation flow constructs typed PostGIS geometry tables.

Segments:

```sql
CREATE TABLE rtdl_v0_2_postgis.segments AS
SELECT
    id,
    ST_GeomFromText(
        'LINESTRING(' || x0 || ' ' || y0 || ',' || x1 || ' ' || y1 || ')',
        4326
    )::geometry(LINESTRING, 4326) AS geom
FROM rtdl_v0_2_postgis.segments_raw;
```

Polygons:

```sql
CREATE TABLE rtdl_v0_2_postgis.polygons AS
SELECT
    id,
    ST_GeomFromText(wkt, 4326)::geometry(POLYGON, 4326) AS geom
FROM rtdl_v0_2_postgis.polygons_raw;
```

Then both geometry tables are indexed and analyzed:

```sql
CREATE INDEX segments_geom_idx
ON rtdl_v0_2_postgis.segments
USING GIST (geom);

CREATE INDEX polygons_geom_idx
ON rtdl_v0_2_postgis.polygons
USING GIST (geom);

ANALYZE rtdl_v0_2_postgis.segments;
ANALYZE rtdl_v0_2_postgis.polygons;
```

## Workload query: `segment_polygon_hitcount`

This is the exact PostGIS query used as the correctness anchor:

```sql
SELECT
    s.id::BIGINT AS segment_id,
    COUNT(p.id)::BIGINT AS hit_count
FROM rtdl_v0_2_postgis.segments AS s
LEFT JOIN rtdl_v0_2_postgis.polygons AS p
    ON ST_Intersects(s.geom, p.geom)
GROUP BY s.id
ORDER BY s.id;
```

Important details:

- `LEFT JOIN` is required
- that keeps zero-hit segments in the output
- the emitted shape is one row per segment

## Workload query: `segment_polygon_anyhit_rows`

This is the exact PostGIS row-materialization query:

```sql
SELECT
    s.id::BIGINT AS segment_id,
    p.id::BIGINT AS polygon_id
FROM rtdl_v0_2_postgis.segments AS s
JOIN rtdl_v0_2_postgis.polygons AS p
    ON ST_Intersects(s.geom, p.geom)
ORDER BY s.id, p.id;
```

Important details:

- plain `JOIN` is used
- zero-hit segments are intentionally omitted
- the emitted shape is one row per true hit pair

## How execution happens in the current harness

Hitcount path:

- [goal114_segment_polygon_postgis.py](/Users/rl2025/rtdl_python_only/src/rtdsl/goal114_segment_polygon_postgis.py)

Any-hit path:

- [goal128_segment_polygon_anyhit_postgis.py](/Users/rl2025/rtdl_python_only/src/rtdsl/goal128_segment_polygon_anyhit_postgis.py)

Execution pattern:

1. load representative RTDL dataset
2. open PostGIS connection
3. drop and recreate per-goal schema
4. create raw tables
5. bulk-load raw rows with `COPY`
6. build typed geometry tables
7. create GiST indexes
8. `ANALYZE`
9. execute the workload query
10. compare RTDL backend rows against the PostGIS result

## Why this matters

This PostGIS path is the independent correctness anchor for the current RTDL
v0.2 segment/polygon families.

It is not:

- an abstract SQL sketch
- a different dataset
- a different geometry problem

It is the actual relational/PostGIS version of the same representative RTDL
workloads used in the current v0.2 validation flow.
