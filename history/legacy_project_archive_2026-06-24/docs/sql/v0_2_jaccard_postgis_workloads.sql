-- RTDL v0.2 PostGIS workload file for the narrow Jaccard line.
--
-- This file preserves the exact SQL shapes used by:
--   - Goal 138: polygon_pair_overlap_area_rows
--   - Goal 140: polygon_set_jaccard
--   - Goal 141: public-data-derived polygon_set_jaccard audit
--
-- Important boundary:
--   - polygon_pair_overlap_area_rows uses ordinary polygon intersection area
--     on the authored orthogonal polygons.
--   - polygon_set_jaccard in RTDL is the narrow unit-cell workload. Its
--     PostGIS checker therefore enumerates covered unit cells and counts them.

BEGIN;

DROP SCHEMA IF EXISTS rtdl_v0_2_jaccard_postgis CASCADE;
CREATE SCHEMA rtdl_v0_2_jaccard_postgis;

-- Expected raw rows for both sides:
--   id BIGINT
--   wkt TEXT
--
-- `wkt` is a POLYGON WKT string such as:
--   POLYGON((x0 y0,x1 y1,x2 y2,...,x0 y0))

CREATE TABLE rtdl_v0_2_jaccard_postgis.left_polygons_raw (
    id BIGINT,
    wkt TEXT
);

CREATE TABLE rtdl_v0_2_jaccard_postgis.right_polygons_raw (
    id BIGINT,
    wkt TEXT
);

-- The Python harness bulk-loads the raw tables with COPY FROM STDIN.
-- After the raw rows exist, build typed geometry tables:

CREATE TABLE rtdl_v0_2_jaccard_postgis.left_polygons AS
SELECT
    id,
    ST_GeomFromText(wkt, 0)::geometry(POLYGON) AS geom
FROM rtdl_v0_2_jaccard_postgis.left_polygons_raw;

CREATE TABLE rtdl_v0_2_jaccard_postgis.right_polygons AS
SELECT
    id,
    ST_GeomFromText(wkt, 0)::geometry(POLYGON) AS geom
FROM rtdl_v0_2_jaccard_postgis.right_polygons_raw;

CREATE INDEX left_polygons_geom_idx
ON rtdl_v0_2_jaccard_postgis.left_polygons
USING GIST (geom);

CREATE INDEX right_polygons_geom_idx
ON rtdl_v0_2_jaccard_postgis.right_polygons
USING GIST (geom);

ANALYZE rtdl_v0_2_jaccard_postgis.left_polygons;
ANALYZE rtdl_v0_2_jaccard_postgis.right_polygons;

-- Workload 1: polygon_pair_overlap_area_rows
--
-- Emit one row per overlapping polygon pair on the authored orthogonal example.
-- This query uses ordinary PostGIS polygon intersection area and matches the
-- narrower authored overlap-row closure package.

CREATE OR REPLACE VIEW rtdl_v0_2_jaccard_postgis.polygon_pair_overlap_area_rows AS
SELECT
    l.id::BIGINT AS left_polygon_id,
    r.id::BIGINT AS right_polygon_id,
    ROUND(ST_Area(ST_Intersection(l.geom, r.geom)))::BIGINT AS intersection_area,
    ROUND(ST_Area(l.geom))::BIGINT AS left_area,
    ROUND(ST_Area(r.geom))::BIGINT AS right_area,
    ROUND(ST_Area(l.geom) + ST_Area(r.geom) - ST_Area(ST_Intersection(l.geom, r.geom)))::BIGINT AS union_area
FROM rtdl_v0_2_jaccard_postgis.left_polygons AS l
JOIN rtdl_v0_2_jaccard_postgis.right_polygons AS r
    ON ST_Intersects(l.geom, r.geom)
WHERE ST_Area(ST_Intersection(l.geom, r.geom)) > 0.0
ORDER BY l.id, r.id;

-- Direct execution form used by Goal 138:

SELECT
    l.id::BIGINT AS left_polygon_id,
    r.id::BIGINT AS right_polygon_id,
    ROUND(ST_Area(ST_Intersection(l.geom, r.geom)))::BIGINT AS intersection_area,
    ROUND(ST_Area(l.geom))::BIGINT AS left_area,
    ROUND(ST_Area(r.geom))::BIGINT AS right_area,
    ROUND(ST_Area(l.geom) + ST_Area(r.geom) - ST_Area(ST_Intersection(l.geom, r.geom)))::BIGINT AS union_area
FROM rtdl_v0_2_jaccard_postgis.left_polygons AS l
JOIN rtdl_v0_2_jaccard_postgis.right_polygons AS r
    ON ST_Intersects(l.geom, r.geom)
WHERE ST_Area(ST_Intersection(l.geom, r.geom)) > 0.0
ORDER BY l.id, r.id;

-- Workload 2: polygon_set_jaccard
--
-- This is the narrow RTDL unit-cell contract, not generic continuous polygon
-- Jaccard. PostGIS therefore enumerates integer grid cells and checks whether
-- the cell center is covered by either polygon set.

WITH cell_bounds AS (
    SELECT
        FLOOR(LEAST(
            (SELECT MIN(ST_XMin(geom)) FROM rtdl_v0_2_jaccard_postgis.left_polygons),
            (SELECT MIN(ST_XMin(geom)) FROM rtdl_v0_2_jaccard_postgis.right_polygons)
        ))::INT AS min_x,
        CEIL(GREATEST(
            (SELECT MAX(ST_XMax(geom)) FROM rtdl_v0_2_jaccard_postgis.left_polygons),
            (SELECT MAX(ST_XMax(geom)) FROM rtdl_v0_2_jaccard_postgis.right_polygons)
        ))::INT AS max_x,
        FLOOR(LEAST(
            (SELECT MIN(ST_YMin(geom)) FROM rtdl_v0_2_jaccard_postgis.left_polygons),
            (SELECT MIN(ST_YMin(geom)) FROM rtdl_v0_2_jaccard_postgis.right_polygons)
        ))::INT AS min_y,
        CEIL(GREATEST(
            (SELECT MAX(ST_YMax(geom)) FROM rtdl_v0_2_jaccard_postgis.left_polygons),
            (SELECT MAX(ST_YMax(geom)) FROM rtdl_v0_2_jaccard_postgis.right_polygons)
        ))::INT AS max_y
),
cells AS (
    SELECT x, y
    FROM cell_bounds,
    generate_series(min_x, max_x - 1) AS x,
    generate_series(min_y, max_y - 1) AS y
),
left_cells AS (
    SELECT DISTINCT c.x, c.y
    FROM cells AS c
    JOIN rtdl_v0_2_jaccard_postgis.left_polygons AS p
      ON ST_Covers(p.geom, ST_SetSRID(ST_Point(c.x + 0.5, c.y + 0.5), 0))
),
right_cells AS (
    SELECT DISTINCT c.x, c.y
    FROM cells AS c
    JOIN rtdl_v0_2_jaccard_postgis.right_polygons AS p
      ON ST_Covers(p.geom, ST_SetSRID(ST_Point(c.x + 0.5, c.y + 0.5), 0))
),
stats AS (
    SELECT
        (SELECT COUNT(*) FROM left_cells) AS left_area,
        (SELECT COUNT(*) FROM right_cells) AS right_area,
        (
            SELECT COUNT(*)
            FROM left_cells AS l
            JOIN right_cells AS r
              ON l.x = r.x AND l.y = r.y
        ) AS intersection_area,
        (
            SELECT COUNT(*)
            FROM (
                SELECT x, y FROM left_cells
                UNION
                SELECT x, y FROM right_cells
            ) AS u
        ) AS union_area
)
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

COMMIT;
