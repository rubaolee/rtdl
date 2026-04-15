from __future__ import annotations

import importlib.util
import os

from .graph_reference import CSRGraph
from .graph_reference import EdgeSeed
from .graph_reference import FrontierVertex
from .graph_reference import normalize_edge_set
from .graph_reference import normalize_frontier
from .graph_reference import normalize_vertex_set
from .graph_reference import validate_csr_graph


def postgresql_available() -> bool:
    return importlib.util.find_spec("psycopg2") is not None


def connect_postgresql(dsn: str | None = None):
    resolved_dsn = (
        dsn
        or os.environ.get("RTDL_POSTGRESQL_DSN")
        or os.environ.get("RTDL_POSTGIS_DSN")
        or "dbname=postgres"
    )
    if not postgresql_available():
        raise RuntimeError(
            "psycopg2 is not installed; install psycopg2 to run the PostgreSQL graph baseline"
        )

    import psycopg2

    return psycopg2.connect(resolved_dsn)


def build_postgresql_bfs_expand_sql(
    *,
    edge_table: str = "rtdl_graph_edges_tmp",
    frontier_table: str = "rtdl_frontier_tmp",
    visited_table: str = "rtdl_visited_tmp",
    dedupe: bool = True,
) -> str:
    if dedupe:
        return f"""
WITH candidates AS (
    SELECT
        f.frontier_pos,
        f.vertex_id AS src_vertex,
        e.dst AS dst_vertex,
        f.level + 1 AS level
    FROM {frontier_table} AS f
    JOIN {edge_table} AS e
      ON e.src = f.vertex_id
    LEFT JOIN {visited_table} AS v
      ON v.vertex_id = e.dst
    WHERE v.vertex_id IS NULL
),
deduped AS (
    SELECT DISTINCT ON (dst_vertex)
        src_vertex,
        dst_vertex,
        level
    FROM candidates
    ORDER BY dst_vertex, frontier_pos, src_vertex
)
SELECT src_vertex, dst_vertex, level
FROM deduped
ORDER BY level, dst_vertex, src_vertex
""".strip()

    return f"""
SELECT
    f.vertex_id AS src_vertex,
    e.dst AS dst_vertex,
    f.level + 1 AS level
FROM {frontier_table} AS f
JOIN {edge_table} AS e
  ON e.src = f.vertex_id
LEFT JOIN {visited_table} AS v
  ON v.vertex_id = e.dst
WHERE v.vertex_id IS NULL
ORDER BY level, dst_vertex, src_vertex
""".strip()


def build_postgresql_triangle_probe_sql(
    *,
    edge_table: str = "rtdl_graph_edges_tmp",
    seed_table: str = "rtdl_edge_seeds_tmp",
    order: str = "id_ascending",
    unique: bool = True,
) -> str:
    if order != "id_ascending":
        raise ValueError("PostgreSQL triangle probe currently supports only order='id_ascending'")

    if unique:
        return f"""
WITH triangles AS (
    SELECT DISTINCT
        s.u AS u,
        s.v AS v,
        eu.dst AS w
    FROM {seed_table} AS s
    JOIN {edge_table} AS eu
      ON eu.src = s.u
    JOIN {edge_table} AS ev
      ON ev.src = s.v
     AND ev.dst = eu.dst
    WHERE s.u <> s.v
      AND s.u < s.v
      AND s.v < eu.dst
)
SELECT u, v, w
FROM triangles
ORDER BY u, v, w
""".strip()

    return f"""
SELECT
    s.u AS u,
    s.v AS v,
    eu.dst AS w
FROM {seed_table} AS s
JOIN {edge_table} AS eu
  ON eu.src = s.u
JOIN {edge_table} AS ev
  ON ev.src = s.v
 AND ev.dst = eu.dst
WHERE s.u <> s.v
  AND s.u < s.v
  AND s.v < eu.dst
ORDER BY u, v, w
""".strip()


def prepare_postgresql_graph_tables(
    connection,
    graph: CSRGraph,
    *,
    edge_table: str = "rtdl_graph_edges_tmp",
) -> None:
    validate_csr_graph(graph)
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"""
CREATE TEMP TABLE {edge_table} (
    src INTEGER NOT NULL,
    dst INTEGER NOT NULL
) ON COMMIT DROP
""".strip()
        )
        edge_rows: list[tuple[int, int]] = []
        for src_vertex in range(graph.vertex_count):
            start = graph.row_offsets[src_vertex]
            end = graph.row_offsets[src_vertex + 1]
            for dst_vertex in graph.column_indices[start:end]:
                edge_rows.append((src_vertex, int(dst_vertex)))
        cursor.executemany(
            f"INSERT INTO {edge_table} (src, dst) VALUES (%s, %s)",
            edge_rows,
        )
        cursor.execute(f"CREATE INDEX {edge_table}_src_idx ON {edge_table} (src)")
        cursor.execute(f"CREATE INDEX {edge_table}_dst_idx ON {edge_table} (dst)")
        cursor.execute(f"CREATE INDEX {edge_table}_src_dst_idx ON {edge_table} (src, dst)")
        cursor.execute(f"ANALYZE {edge_table}")
    finally:
        cursor.close()


def prepare_postgresql_bfs_inputs(
    connection,
    frontier,
    visited,
    *,
    frontier_table: str = "rtdl_frontier_tmp",
    visited_table: str = "rtdl_visited_tmp",
) -> None:
    frontier_rows = normalize_frontier(frontier)
    visited_rows = normalize_vertex_set(visited)
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"""
CREATE TEMP TABLE {frontier_table} (
    frontier_pos INTEGER NOT NULL,
    vertex_id INTEGER NOT NULL,
    level INTEGER NOT NULL
) ON COMMIT DROP
""".strip()
        )
        cursor.execute(
            f"""
CREATE TEMP TABLE {visited_table} (
    vertex_id INTEGER NOT NULL
) ON COMMIT DROP
""".strip()
        )
        cursor.executemany(
            f"INSERT INTO {frontier_table} (frontier_pos, vertex_id, level) VALUES (%s, %s, %s)",
            [(position, row.vertex_id, row.level) for position, row in enumerate(frontier_rows)],
        )
        cursor.executemany(
            f"INSERT INTO {visited_table} (vertex_id) VALUES (%s)",
            [(vertex_id,) for vertex_id in visited_rows],
        )
        cursor.execute(f"CREATE INDEX {frontier_table}_vertex_idx ON {frontier_table} (vertex_id)")
        cursor.execute(f"CREATE INDEX {visited_table}_vertex_idx ON {visited_table} (vertex_id)")
        cursor.execute(f"ANALYZE {frontier_table}")
        cursor.execute(f"ANALYZE {visited_table}")
    finally:
        cursor.close()


def prepare_postgresql_triangle_inputs(
    connection,
    seeds,
    *,
    seed_table: str = "rtdl_edge_seeds_tmp",
) -> None:
    seed_rows = normalize_edge_set(seeds)
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"""
CREATE TEMP TABLE {seed_table} (
    seed_pos INTEGER NOT NULL,
    u INTEGER NOT NULL,
    v INTEGER NOT NULL
) ON COMMIT DROP
""".strip()
        )
        cursor.executemany(
            f"INSERT INTO {seed_table} (seed_pos, u, v) VALUES (%s, %s, %s)",
            [(position, row.u, row.v) for position, row in enumerate(seed_rows)],
        )
        cursor.execute(f"CREATE INDEX {seed_table}_uv_idx ON {seed_table} (u, v)")
        cursor.execute(f"ANALYZE {seed_table}")
    finally:
        cursor.close()


def query_postgresql_bfs_expand(
    connection,
    *,
    edge_table: str = "rtdl_graph_edges_tmp",
    frontier_table: str = "rtdl_frontier_tmp",
    visited_table: str = "rtdl_visited_tmp",
    dedupe: bool = True,
) -> tuple[dict[str, int], ...]:
    cursor = connection.cursor()
    try:
        cursor.execute(
            build_postgresql_bfs_expand_sql(
                edge_table=edge_table,
                frontier_table=frontier_table,
                visited_table=visited_table,
                dedupe=dedupe,
            )
        )
        return tuple(
            {
                "src_vertex": int(src_vertex),
                "dst_vertex": int(dst_vertex),
                "level": int(level),
            }
            for src_vertex, dst_vertex, level in cursor.fetchall()
        )
    finally:
        cursor.close()


def query_postgresql_triangle_probe(
    connection,
    *,
    edge_table: str = "rtdl_graph_edges_tmp",
    seed_table: str = "rtdl_edge_seeds_tmp",
    order: str = "id_ascending",
    unique: bool = True,
) -> tuple[dict[str, int], ...]:
    cursor = connection.cursor()
    try:
        cursor.execute(
            build_postgresql_triangle_probe_sql(
                edge_table=edge_table,
                seed_table=seed_table,
                order=order,
                unique=unique,
            )
        )
        return tuple(
            {
                "u": int(u),
                "v": int(v),
                "w": int(w),
            }
            for u, v, w in cursor.fetchall()
        )
    finally:
        cursor.close()


def run_postgresql_bfs_expand(
    connection,
    graph: CSRGraph,
    frontier,
    visited,
    *,
    edge_table: str = "rtdl_graph_edges_tmp",
    frontier_table: str = "rtdl_frontier_tmp",
    visited_table: str = "rtdl_visited_tmp",
    dedupe: bool = True,
) -> tuple[dict[str, int], ...]:
    prepare_postgresql_graph_tables(connection, graph, edge_table=edge_table)
    prepare_postgresql_bfs_inputs(
        connection,
        frontier,
        visited,
        frontier_table=frontier_table,
        visited_table=visited_table,
    )
    return query_postgresql_bfs_expand(
        connection,
        edge_table=edge_table,
        frontier_table=frontier_table,
        visited_table=visited_table,
        dedupe=dedupe,
    )


def run_postgresql_triangle_probe(
    connection,
    graph: CSRGraph,
    seeds,
    *,
    edge_table: str = "rtdl_graph_edges_tmp",
    seed_table: str = "rtdl_edge_seeds_tmp",
    order: str = "id_ascending",
    unique: bool = True,
) -> tuple[dict[str, int], ...]:
    prepare_postgresql_graph_tables(connection, graph, edge_table=edge_table)
    prepare_postgresql_triangle_inputs(
        connection,
        seeds,
        seed_table=seed_table,
    )
    return query_postgresql_triangle_probe(
        connection,
        edge_table=edge_table,
        seed_table=seed_table,
        order=order,
        unique=unique,
    )
