-- RTDL v0.4 application comparison script: event hotspot screening.
--
-- Expected raw table:
--   events_raw(id BIGINT, x DOUBLE PRECISION, y DOUBLE PRECISION)
--
-- Optional psql variables:
--   \set radius 0.75
--   \set k_max 12
--   \set hotspot_threshold 3

\if :{?radius}
\else
\set radius 0.75
\endif

\if :{?k_max}
\else
\set k_max 12
\endif

\if :{?hotspot_threshold}
\else
\set hotspot_threshold 3
\endif

BEGIN;

DROP SCHEMA IF EXISTS rtdl_v0_4_event_hotspot CASCADE;
CREATE SCHEMA rtdl_v0_4_event_hotspot;

CREATE TABLE rtdl_v0_4_event_hotspot.events AS
SELECT id, ST_SetSRID(ST_MakePoint(x, y), 0)::geometry(Point, 0) AS geom
FROM events_raw;

CREATE INDEX events_geom_idx ON rtdl_v0_4_event_hotspot.events USING GIST (geom);
ANALYZE rtdl_v0_4_event_hotspot.events;

WITH ranked_neighbors AS (
    SELECT
        q.id AS query_id,
        s.id AS neighbor_id,
        ST_Distance(q.geom, s.geom) AS distance,
        ROW_NUMBER() OVER (
            PARTITION BY q.id
            ORDER BY ST_Distance(q.geom, s.geom), s.id
        ) AS neighbor_rank
    FROM rtdl_v0_4_event_hotspot.events AS q
    JOIN rtdl_v0_4_event_hotspot.events AS s
      ON ST_DWithin(q.geom, s.geom, :radius)
    WHERE q.id <> s.id
)
SELECT query_id, neighbor_id, distance
FROM ranked_neighbors
WHERE neighbor_rank <= :k_max
ORDER BY query_id, distance, neighbor_id;

SELECT
    q.id AS event_id,
    COUNT(s.id)::BIGINT AS neighbor_count
FROM rtdl_v0_4_event_hotspot.events AS q
LEFT JOIN rtdl_v0_4_event_hotspot.events AS s
  ON q.id <> s.id
 AND ST_DWithin(q.geom, s.geom, :radius)
GROUP BY q.id
HAVING COUNT(s.id) >= :hotspot_threshold
ORDER BY neighbor_count DESC, event_id;

COMMIT;
