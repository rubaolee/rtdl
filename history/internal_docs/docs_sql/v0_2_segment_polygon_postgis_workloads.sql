-- RTDL v0.2 PostGIS workload file for the two closed segment/polygon families.
--
-- This file contains the actual PostGIS table-building and query shape used by
-- the RTDL v0.2 validation flow.
--
-- The Python harness feeds the raw tables with COPY FROM STDIN. This file
-- describes the SQL side once those raw rows are present.

BEGIN;

DROP SCHEMA IF EXISTS rtdl_v0_2_postgis CASCADE;
CREATE SCHEMA rtdl_v0_2_postgis;

-- Expected raw probe rows:
--   id BIGINT
--   x0 DOUBLE PRECISION
--   y0 DOUBLE PRECISION
--   x1 DOUBLE PRECISION
--   y1 DOUBLE PRECISION
CREATE TABLE rtdl_v0_2_postgis.segments_raw (
    id BIGINT,
    x0 DOUBLE PRECISION,
    y0 DOUBLE PRECISION,
    x1 DOUBLE PRECISION,
    y1 DOUBLE PRECISION
);

-- Expected raw build rows:
--   id BIGINT
--   wkt TEXT
--
-- `wkt` is a POLYGON WKT string such as:
--   POLYGON((x0 y0,x1 y1,x2 y2,...,x0 y0))
CREATE TABLE rtdl_v0_2_postgis.polygons_raw (
    id BIGINT,
    wkt TEXT
);

-- The Python harness bulk-loads both raw tables with COPY FROM STDIN.
--
-- After the raw rows exist, build typed geometry tables:

CREATE TABLE rtdl_v0_2_postgis.segments AS
SELECT
    id,
    ST_GeomFromText(
        'LINESTRING(' || x0 || ' ' || y0 || ',' || x1 || ' ' || y1 || ')',
        4326
    )::geometry(LINESTRING, 4326) AS geom
FROM rtdl_v0_2_postgis.segments_raw;

CREATE TABLE rtdl_v0_2_postgis.polygons AS
SELECT
    id,
    ST_GeomFromText(wkt, 4326)::geometry(POLYGON, 4326) AS geom
FROM rtdl_v0_2_postgis.polygons_raw;

CREATE INDEX segments_geom_idx
ON rtdl_v0_2_postgis.segments
USING GIST (geom);

CREATE INDEX polygons_geom_idx
ON rtdl_v0_2_postgis.polygons
USING GIST (geom);

ANALYZE rtdl_v0_2_postgis.segments;
ANALYZE rtdl_v0_2_postgis.polygons;

-- Workload 1: segment_polygon_hitcount
--
-- Emit one row per segment with the number of polygons that intersect it.
-- LEFT JOIN is required so zero-hit segments remain in the output.

CREATE OR REPLACE VIEW rtdl_v0_2_postgis.segment_polygon_hitcount AS
SELECT
    s.id::BIGINT AS segment_id,
    COUNT(p.id)::BIGINT AS hit_count
FROM rtdl_v0_2_postgis.segments AS s
LEFT JOIN rtdl_v0_2_postgis.polygons AS p
    ON ST_Intersects(s.geom, p.geom)
GROUP BY s.id
ORDER BY s.id;

-- Workload 2: segment_polygon_anyhit_rows
--
-- Emit one row per true segment/polygon intersection.
-- JOIN is used here because zero-hit segments are intentionally omitted.

CREATE OR REPLACE VIEW rtdl_v0_2_postgis.segment_polygon_anyhit_rows AS
SELECT
    s.id::BIGINT AS segment_id,
    p.id::BIGINT AS polygon_id
FROM rtdl_v0_2_postgis.segments AS s
JOIN rtdl_v0_2_postgis.polygons AS p
    ON ST_Intersects(s.geom, p.geom)
ORDER BY s.id, p.id;

-- Direct execution forms used by the validation path:

SELECT
    s.id::BIGINT AS segment_id,
    COUNT(p.id)::BIGINT AS hit_count
FROM rtdl_v0_2_postgis.segments AS s
LEFT JOIN rtdl_v0_2_postgis.polygons AS p
    ON ST_Intersects(s.geom, p.geom)
GROUP BY s.id
ORDER BY s.id;

SELECT
    s.id::BIGINT AS segment_id,
    p.id::BIGINT AS polygon_id
FROM rtdl_v0_2_postgis.segments AS s
JOIN rtdl_v0_2_postgis.polygons AS p
    ON ST_Intersects(s.geom, p.geom)
ORDER BY s.id, p.id;

COMMIT;
