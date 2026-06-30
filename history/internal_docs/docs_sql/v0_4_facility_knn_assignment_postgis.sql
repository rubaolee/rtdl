-- RTDL v0.4 application comparison script: facility k-nearest assignment.
--
-- Expected raw tables:
--   customers_raw(id BIGINT, x DOUBLE PRECISION, y DOUBLE PRECISION)
--   depots_raw(id BIGINT, x DOUBLE PRECISION, y DOUBLE PRECISION)
--
-- Optional psql variable:
--   \set k 3

\if :{?k}
\else
\set k 3
\endif

BEGIN;

DROP SCHEMA IF EXISTS rtdl_v0_4_facility_knn CASCADE;
CREATE SCHEMA rtdl_v0_4_facility_knn;

CREATE TABLE rtdl_v0_4_facility_knn.customers AS
SELECT id, ST_SetSRID(ST_MakePoint(x, y), 0)::geometry(Point, 0) AS geom
FROM customers_raw;

CREATE TABLE rtdl_v0_4_facility_knn.depots AS
SELECT id, ST_SetSRID(ST_MakePoint(x, y), 0)::geometry(Point, 0) AS geom
FROM depots_raw;

CREATE INDEX customers_geom_idx ON rtdl_v0_4_facility_knn.customers USING GIST (geom);
CREATE INDEX depots_geom_idx ON rtdl_v0_4_facility_knn.depots USING GIST (geom);

ANALYZE rtdl_v0_4_facility_knn.customers;
ANALYZE rtdl_v0_4_facility_knn.depots;

SELECT
    c.id AS query_id,
    ranked.neighbor_id,
    ranked.distance,
    ranked.neighbor_rank
FROM rtdl_v0_4_facility_knn.customers AS c
CROSS JOIN LATERAL (
    SELECT
        ranked_inner.neighbor_id,
        ranked_inner.distance,
        ranked_inner.neighbor_rank
    FROM (
        SELECT
            d.id AS neighbor_id,
            ST_Distance(c.geom, d.geom) AS distance,
            ROW_NUMBER() OVER (
                ORDER BY ST_Distance(c.geom, d.geom), d.id
            ) AS neighbor_rank
        FROM rtdl_v0_4_facility_knn.depots AS d
        ORDER BY c.geom <-> d.geom, ST_Distance(c.geom, d.geom), d.id
        LIMIT :k
    ) AS ranked_inner
    ORDER BY ranked_inner.neighbor_rank
) AS ranked
ORDER BY query_id, neighbor_rank;

COMMIT;
