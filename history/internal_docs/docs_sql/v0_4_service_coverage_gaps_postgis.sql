-- RTDL v0.4 application comparison script: service coverage gaps.
--
-- Expected raw tables:
--   households_raw(id BIGINT, x DOUBLE PRECISION, y DOUBLE PRECISION)
--   clinics_raw(id BIGINT, x DOUBLE PRECISION, y DOUBLE PRECISION)
--
-- Optional psql variables:
--   \set radius 0.85
--   \set k_max 4

\if :{?radius}
\else
\set radius 0.85
\endif

\if :{?k_max}
\else
\set k_max 4
\endif

BEGIN;

DROP SCHEMA IF EXISTS rtdl_v0_4_service_coverage CASCADE;
CREATE SCHEMA rtdl_v0_4_service_coverage;

CREATE TABLE rtdl_v0_4_service_coverage.households AS
SELECT id, ST_SetSRID(ST_MakePoint(x, y), 0)::geometry(Point, 0) AS geom
FROM households_raw;

CREATE TABLE rtdl_v0_4_service_coverage.clinics AS
SELECT id, ST_SetSRID(ST_MakePoint(x, y), 0)::geometry(Point, 0) AS geom
FROM clinics_raw;

CREATE INDEX households_geom_idx ON rtdl_v0_4_service_coverage.households USING GIST (geom);
CREATE INDEX clinics_geom_idx ON rtdl_v0_4_service_coverage.clinics USING GIST (geom);

ANALYZE rtdl_v0_4_service_coverage.households;
ANALYZE rtdl_v0_4_service_coverage.clinics;

WITH ranked_neighbors AS (
    SELECT
        h.id AS query_id,
        c.id AS neighbor_id,
        ST_Distance(h.geom, c.geom) AS distance,
        ROW_NUMBER() OVER (
            PARTITION BY h.id
            ORDER BY ST_Distance(h.geom, c.geom), c.id
        ) AS neighbor_rank
    FROM rtdl_v0_4_service_coverage.households AS h
    JOIN rtdl_v0_4_service_coverage.clinics AS c
      ON ST_DWithin(h.geom, c.geom, :radius)
)
SELECT query_id, neighbor_id, distance
FROM ranked_neighbors
WHERE neighbor_rank <= :k_max
ORDER BY query_id, distance, neighbor_id;

SELECT h.id AS household_id
FROM rtdl_v0_4_service_coverage.households AS h
LEFT JOIN rtdl_v0_4_service_coverage.clinics AS c
  ON ST_DWithin(h.geom, c.geom, :radius)
WHERE c.id IS NULL
ORDER BY household_id;

COMMIT;
