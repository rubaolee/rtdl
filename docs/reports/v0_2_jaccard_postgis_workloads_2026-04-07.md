# RTDL v0.2 Jaccard PostGIS Workloads

Date: 2026-04-07
Status: accepted reference note

Main SQL artifact:

- [v0_2_jaccard_postgis_workloads.sql](/Users/rl2025/rtdl_python_only/docs/sql/v0_2_jaccard_postgis_workloads.sql)

## What this file is

This note preserves the actual PostGIS SQL workload shapes used by the narrow
RTDL Jaccard line.

It covers:

- table building
- indexes
- pairwise overlap query
- aggregate Jaccard query
- the important semantic difference between:
  - ordinary authored overlap-area rows
  - narrow unit-cell Jaccard checking

The two Jaccard-line workloads covered are:

- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

## Raw data shape

Both sides are loaded into raw tables as:

```sql
CREATE TABLE ...left_polygons_raw (
    id BIGINT,
    wkt TEXT
);

CREATE TABLE ...right_polygons_raw (
    id BIGINT,
    wkt TEXT
);
```

The Python harness bulk-loads these with `COPY FROM STDIN`.

The typed geometry tables are then built with:

```sql
CREATE TABLE ...left_polygons AS
SELECT id, ST_GeomFromText(wkt, 0)::geometry(POLYGON) AS geom
FROM ...left_polygons_raw;

CREATE TABLE ...right_polygons AS
SELECT id, ST_GeomFromText(wkt, 0)::geometry(POLYGON) AS geom
FROM ...right_polygons_raw;
```

Both geometry tables are indexed:

```sql
CREATE INDEX left_polygons_geom_idx
ON ...left_polygons
USING GIST (geom);

CREATE INDEX right_polygons_geom_idx
ON ...right_polygons
USING GIST (geom);

ANALYZE ...left_polygons;
ANALYZE ...right_polygons;
```

## Query 1: pairwise overlap rows

The authored Goal 138 overlap-row checker uses ordinary PostGIS polygon
intersection area:

```sql
SELECT
    l.id::BIGINT AS left_polygon_id,
    r.id::BIGINT AS right_polygon_id,
    ROUND(ST_Area(ST_Intersection(l.geom, r.geom)))::BIGINT AS intersection_area,
    ROUND(ST_Area(l.geom))::BIGINT AS left_area,
    ROUND(ST_Area(r.geom))::BIGINT AS right_area,
    ROUND(ST_Area(l.geom) + ST_Area(r.geom) - ST_Area(ST_Intersection(l.geom, r.geom)))::BIGINT AS union_area
FROM ...left_polygons AS l
JOIN ...right_polygons AS r
    ON ST_Intersects(l.geom, r.geom)
WHERE ST_Area(ST_Intersection(l.geom, r.geom)) > 0.0
ORDER BY l.id, r.id;
```

This is acceptable because the authored closure package uses small orthogonal
polygons and the parity story there is pairwise overlap rows, not the later
public-data-derived unit-cell aggregate.

## Query 2: aggregate narrow Jaccard

The RTDL Jaccard feature is not generic continuous polygon Jaccard.

Its accepted contract is:

- orthogonal integer-grid polygons
- area measured as covered `1x1` unit cells

So the PostGIS checker does **not** use `ST_Area(ST_Intersection(...))` as the
final meaning of Jaccard.

Instead it:

1. computes integer cell bounds
2. enumerates all grid cells in that range
3. tests cell-center coverage with `ST_Covers`
4. builds:
   - `left_cells`
   - `right_cells`
5. counts:
   - left area
   - right area
   - intersection
   - union

Core query shape:

```sql
WITH cell_bounds AS (...),
cells AS (... generate_series ...),
left_cells AS (
    SELECT DISTINCT c.x, c.y
    FROM cells AS c
    JOIN ...left_polygons AS p
      ON ST_Covers(p.geom, ST_SetSRID(ST_Point(c.x + 0.5, c.y + 0.5), 0))
),
right_cells AS (
    SELECT DISTINCT c.x, c.y
    FROM cells AS c
    JOIN ...right_polygons AS p
      ON ST_Covers(p.geom, ST_SetSRID(ST_Point(c.x + 0.5, c.y + 0.5), 0))
),
stats AS (...)
SELECT
    intersection_area::BIGINT,
    left_area::BIGINT,
    right_area::BIGINT,
    union_area::BIGINT,
    CASE
        WHEN union_area = 0 THEN 0.0
        ELSE intersection_area::DOUBLE PRECISION / union_area::DOUBLE PRECISION
    END AS jaccard_similarity
FROM stats;
```

## Why PostGIS can be slow here

This aggregate checker is expensive because it is effectively doing:

- grid-cell generation
- many `ST_Covers(point)` checks
- dedup of covered cells
- set intersection and union over cell rows

So for the narrow Jaccard line, PostGIS is serving as an external correctness
anchor for the unit-cell semantics, not as a particularly favorable execution
engine for this workload.

## Public-data-derived case

For Goal 141, the same aggregate unit-cell SQL shape was used on the converted
MoNuSeg-derived unit-square polygons.

Important boundary:

- raw MoNuSeg annotations are freehand polygons
- the accepted RTDL workload first converts them into unit-cell square polygons
- the PostGIS checker then runs the same unit-cell aggregate query above

## Why this matters

This SQL file is now the canonical saved answer to:

- what exactly did PostGIS execute for the Jaccard-line correctness checks?

It makes the repo explicit that:

- overlap-area rows and aggregate Jaccard do not use the same PostGIS meaning
- the aggregate Jaccard path is intentionally narrow and unit-cell-based
