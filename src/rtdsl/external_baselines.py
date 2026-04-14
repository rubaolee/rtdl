from __future__ import annotations

import importlib.util
import math
import os

from .graph_reference import CSRGraph
from .reference import Point
from .reference import Point3D


def scipy_available() -> bool:
    return importlib.util.find_spec("scipy") is not None


def postgis_available() -> bool:
    return importlib.util.find_spec("psycopg2") is not None


def _load_ckdtree():
    if not scipy_available():
        raise RuntimeError(
            "SciPy is not installed; install scipy to run the cKDTree external baseline"
        )
    from scipy.spatial import cKDTree

    return cKDTree


def run_scipy_fixed_radius_neighbors(
    query_points: tuple[Point, ...],
    search_points: tuple[Point, ...],
    *,
    radius: float,
    k_max: int,
    tree_factory=None,
) -> tuple[dict[str, float | int], ...]:
    if tree_factory is None:
        tree_factory = _load_ckdtree()

    search_coords = tuple((point.x, point.y) for point in search_points)
    tree = tree_factory(search_coords)
    rows: list[dict[str, float | int]] = []

    for query_point in query_points:
        candidate_indexes = tree.query_ball_point((query_point.x, query_point.y), r=radius)
        candidates: list[tuple[float, int]] = []
        for index in candidate_indexes:
            search_point = search_points[int(index)]
            distance = math.hypot(search_point.x - query_point.x, search_point.y - query_point.y)
            if distance <= radius:
                candidates.append((distance, search_point.id))

        candidates.sort(key=lambda item: (item[0], item[1]))
        for distance, neighbor_id in candidates[:k_max]:
            rows.append(
                {
                    "query_id": query_point.id,
                    "neighbor_id": neighbor_id,
                    "distance": distance,
                }
            )

    rows.sort(key=lambda row: row["query_id"])
    return tuple(rows)


def run_scipy_knn_rows(
    query_points: tuple[Point, ...],
    search_points: tuple[Point, ...],
    *,
    k: int,
    tree_factory=None,
) -> tuple[dict[str, float | int], ...]:
    if tree_factory is None:
        tree_factory = _load_ckdtree()

    if not search_points:
        return ()

    search_coords = tuple((point.x, point.y) for point in search_points)
    tree = tree_factory(search_coords)
    rows: list[dict[str, float | int]] = []
    query_k = min(k, len(search_points))

    for query_point in query_points:
        distances, indexes = tree.query((query_point.x, query_point.y), k=query_k)
        if query_k == 1:
            distance_index_pairs = ((float(distances), int(indexes)),)
        else:
            distance_index_pairs = tuple((float(distance), int(index)) for distance, index in zip(distances, indexes))

        candidates: list[tuple[float, int]] = []
        for distance, index in distance_index_pairs:
            search_point = search_points[index]
            candidates.append((distance, search_point.id))

        candidates.sort(key=lambda item: (item[0], item[1]))
        for rank, (distance, neighbor_id) in enumerate(candidates, start=1):
            rows.append(
                {
                    "query_id": query_point.id,
                    "neighbor_id": neighbor_id,
                    "distance": distance,
                    "neighbor_rank": rank,
                }
            )

    rows.sort(key=lambda row: row["query_id"])
    return tuple(rows)


def connect_postgis(dsn: str | None = None):
    resolved_dsn = dsn or os.environ.get("RTDL_POSTGIS_DSN")
    if not resolved_dsn:
        raise RuntimeError(
            "PostGIS DSN is required; pass postgis_dsn=... or set RTDL_POSTGIS_DSN"
        )
    if not postgis_available():
        raise RuntimeError(
            "psycopg2 is not installed; install psycopg2 to run the PostGIS baseline"
        )

    import psycopg2

    return psycopg2.connect(resolved_dsn)


def postgresql_available() -> bool:
    return postgis_available()


def connect_postgresql(dsn: str | None = None):
    resolved_dsn = dsn or os.environ.get("RTDL_POSTGRESQL_DSN") or os.environ.get("RTDL_POSTGIS_DSN")
    if not resolved_dsn:
        raise RuntimeError(
            "PostgreSQL DSN is required; pass postgresql_dsn=... or set RTDL_POSTGRESQL_DSN"
        )
    if not postgresql_available():
        raise RuntimeError(
            "psycopg2 is not installed; install psycopg2 to run the PostgreSQL baseline"
        )

    import psycopg2

    return psycopg2.connect(resolved_dsn)


def build_postgresql_bfs_levels_sql(
    *,
    edge_table: str = "rtdl_graph_edges_tmp",
) -> str:
    return f"""
WITH RECURSIVE bfs(vertex_id, level) AS (
    SELECT %s::BIGINT AS vertex_id, 0::BIGINT AS level
    UNION
    SELECT e.dst AS vertex_id, bfs.level + 1 AS level
    FROM bfs
    JOIN {edge_table} AS e
      ON e.src = bfs.vertex_id
)
SELECT vertex_id, MIN(level) AS level
FROM bfs
GROUP BY vertex_id
ORDER BY level, vertex_id
""".strip()


def build_postgresql_triangle_count_sql(
    *,
    edge_table: str = "rtdl_graph_edges_tmp",
) -> str:
    return f"""
SELECT COUNT(*)::BIGINT AS triangle_count
FROM {edge_table} AS e1
JOIN {edge_table} AS e2
  ON e1.dst = e2.src
JOIN {edge_table} AS e3
  ON e3.src = e1.src
 AND e3.dst = e2.dst
WHERE e1.src < e1.dst
  AND e2.src < e2.dst
  AND e3.src < e3.dst
  AND e1.src < e2.src
""".strip()


def prepare_postgresql_graph_edges_table(
    connection,
    graph: CSRGraph,
    *,
    edge_table: str = "rtdl_graph_edges_tmp",
    canonical_undirected: bool = False,
) -> None:
    cursor = connection.cursor()
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {edge_table}")
        cursor.execute(
            f"""
CREATE TEMP TABLE {edge_table} (
    src BIGINT NOT NULL,
    dst BIGINT NOT NULL
) ON COMMIT DROP
""".strip()
        )
        if canonical_undirected:
            payload = list(_canonical_undirected_edges(graph))
        else:
            payload = list(_directed_edges(graph))
        cursor.executemany(
            f"INSERT INTO {edge_table} (src, dst) VALUES (%s, %s)",
            payload,
        )
        cursor.execute(f"CREATE INDEX {edge_table}_src_idx ON {edge_table} (src)")
        cursor.execute(f"CREATE INDEX {edge_table}_dst_idx ON {edge_table} (dst)")
        cursor.execute(f"ANALYZE {edge_table}")
    finally:
        cursor.close()


def query_postgresql_bfs_levels(
    connection,
    *,
    source_id: int,
    edge_table: str = "rtdl_graph_edges_tmp",
) -> tuple[dict[str, int], ...]:
    cursor = connection.cursor()
    try:
        cursor.execute(
            build_postgresql_bfs_levels_sql(edge_table=edge_table),
            (int(source_id),),
        )
        rows = cursor.fetchall()
        return tuple(
            {"vertex_id": int(vertex_id), "level": int(level)}
            for vertex_id, level in rows
        )
    finally:
        cursor.close()


def run_postgresql_bfs_levels(
    connection,
    graph: CSRGraph,
    *,
    source_id: int,
    edge_table: str = "rtdl_graph_edges_tmp",
) -> tuple[dict[str, int], ...]:
    prepare_postgresql_graph_edges_table(
        connection,
        graph,
        edge_table=edge_table,
        canonical_undirected=False,
    )
    return query_postgresql_bfs_levels(
        connection,
        source_id=source_id,
        edge_table=edge_table,
    )


def query_postgresql_triangle_count(
    connection,
    *,
    edge_table: str = "rtdl_graph_edges_tmp",
) -> int:
    cursor = connection.cursor()
    try:
        cursor.execute(
            build_postgresql_triangle_count_sql(edge_table=edge_table)
        )
        row = cursor.fetchone()
        if row is None:
            return 0
        return int(row[0])
    finally:
        cursor.close()


def run_postgresql_triangle_count(
    connection,
    graph: CSRGraph,
    *,
    edge_table: str = "rtdl_graph_edges_tmp",
) -> int:
    prepare_postgresql_graph_edges_table(
        connection,
        graph,
        edge_table=edge_table,
        canonical_undirected=True,
    )
    return query_postgresql_triangle_count(
        connection,
        edge_table=edge_table,
    )


def _directed_edges(graph: CSRGraph):
    for src in range(graph.vertex_count):
        start = graph.row_offsets[src]
        stop = graph.row_offsets[src + 1]
        for dst in graph.column_indices[start:stop]:
            yield (int(src), int(dst))


def _canonical_undirected_edges(graph: CSRGraph):
    seen: set[tuple[int, int]] = set()
    for src, dst in _directed_edges(graph):
        left = min(src, dst)
        right = max(src, dst)
        if left == right:
            continue
        edge = (left, right)
        if edge in seen:
            continue
        seen.add(edge)
        yield edge


def build_postgis_fixed_radius_neighbors_sql(
    *,
    query_table: str = "rtdl_query_points_tmp",
    search_table: str = "rtdl_search_points_tmp",
) -> str:
    return f"""
WITH ranked_neighbors AS (
    SELECT
        q.id AS query_id,
        s.id AS neighbor_id,
        ST_Distance(q.geom, s.geom) AS distance,
        ROW_NUMBER() OVER (
            PARTITION BY q.id
            ORDER BY ST_Distance(q.geom, s.geom), s.id
        ) AS neighbor_rank
    FROM {query_table} AS q
    JOIN {search_table} AS s
      ON ST_DWithin(q.geom, s.geom, %s)
)
SELECT query_id, neighbor_id, distance
FROM ranked_neighbors
WHERE neighbor_rank <= %s
ORDER BY query_id, distance, neighbor_id
""".strip()


def build_postgis_fixed_radius_neighbors_3d_sql(
    *,
    query_table: str = "rtdl_query_points3d_tmp",
    search_table: str = "rtdl_search_points3d_tmp",
) -> str:
    return f"""
WITH ranked_neighbors AS (
    SELECT
        q.id AS query_id,
        s.id AS neighbor_id,
        ST_3DDistance(q.geom, s.geom) AS distance,
        ROW_NUMBER() OVER (
            PARTITION BY q.id
            ORDER BY ST_3DDistance(q.geom, s.geom), s.id
        ) AS neighbor_rank
    FROM {query_table} AS q
    JOIN {search_table} AS s
      ON ST_3DDWithin(q.geom, s.geom, %s)
)
SELECT query_id, neighbor_id, distance
FROM ranked_neighbors
WHERE neighbor_rank <= %s
ORDER BY query_id, distance, neighbor_id
""".strip()


def build_postgis_knn_rows_sql(
    *,
    query_table: str = "rtdl_query_points_tmp",
    search_table: str = "rtdl_search_points_tmp",
) -> str:
    return f"""
SELECT
    q.id AS query_id,
    ranked.neighbor_id,
    ranked.distance,
    ranked.neighbor_rank
FROM {query_table} AS q
CROSS JOIN LATERAL (
    SELECT
        ranked_inner.neighbor_id,
        ranked_inner.distance,
        ranked_inner.neighbor_rank
    FROM (
        SELECT
            s.id AS neighbor_id,
            ST_Distance(q.geom, s.geom) AS distance,
            ROW_NUMBER() OVER (
                ORDER BY ST_Distance(q.geom, s.geom), s.id
            ) AS neighbor_rank
        FROM {search_table} AS s
        ORDER BY q.geom <-> s.geom, ST_Distance(q.geom, s.geom), s.id
        LIMIT %s
    ) AS ranked_inner
    ORDER BY ranked_inner.neighbor_rank
) AS ranked
ORDER BY query_id, neighbor_rank
""".strip()


def build_postgis_knn_rows_3d_sql(
    *,
    query_table: str = "rtdl_query_points3d_tmp",
    search_table: str = "rtdl_search_points3d_tmp",
) -> str:
    return f"""
SELECT
    q.id AS query_id,
    ranked.neighbor_id,
    ranked.distance,
    ranked.neighbor_rank
FROM {query_table} AS q
CROSS JOIN LATERAL (
    SELECT
        ranked_inner.neighbor_id,
        ranked_inner.distance,
        ranked_inner.neighbor_rank
    FROM (
        SELECT
            s.id AS neighbor_id,
            ST_3DDistance(q.geom, s.geom) AS distance,
            ROW_NUMBER() OVER (
                ORDER BY ST_3DDistance(q.geom, s.geom), s.id
            ) AS neighbor_rank
        FROM {search_table} AS s
        ORDER BY ST_3DDistance(q.geom, s.geom), s.id
        LIMIT %s
    ) AS ranked_inner
    ORDER BY ranked_inner.neighbor_rank
) AS ranked
ORDER BY query_id, neighbor_rank
""".strip()


def build_postgis_bounded_knn_rows_3d_sql(
    *,
    query_table: str = "rtdl_query_points3d_tmp",
    search_table: str = "rtdl_search_points3d_tmp",
) -> str:
    return f"""
WITH ranked_neighbors AS (
    SELECT
        q.id AS query_id,
        s.id AS neighbor_id,
        ST_3DDistance(q.geom, s.geom) AS distance,
        ROW_NUMBER() OVER (
            PARTITION BY q.id
            ORDER BY ST_3DDistance(q.geom, s.geom), s.id
        ) AS neighbor_rank
    FROM {query_table} AS q
    JOIN {search_table} AS s
      ON ST_3DDWithin(q.geom, s.geom, %s)
)
SELECT query_id, neighbor_id, distance, neighbor_rank
FROM ranked_neighbors
WHERE neighbor_rank <= %s
ORDER BY query_id, neighbor_rank
""".strip()


def run_postgis_fixed_radius_neighbors(
    connection,
    query_points: tuple[Point, ...],
    search_points: tuple[Point, ...],
    *,
    radius: float,
    k_max: int,
    query_table: str = "rtdl_query_points_tmp",
    search_table: str = "rtdl_search_points_tmp",
) -> tuple[dict[str, float | int], ...]:
    prepare_postgis_point_tables(
        connection,
        query_points,
        search_points,
        query_table=query_table,
        search_table=search_table,
    )
    return query_postgis_fixed_radius_neighbors(
        connection,
        radius=radius,
        k_max=k_max,
        query_table=query_table,
        search_table=search_table,
    )


def prepare_postgis_point_tables(
    connection,
    query_points: tuple[Point, ...],
    search_points: tuple[Point, ...],
    *,
    query_table: str = "rtdl_query_points_tmp",
    search_table: str = "rtdl_search_points_tmp",
) -> None:
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"""
CREATE TEMP TABLE {query_table} (
    id BIGINT NOT NULL,
    x DOUBLE PRECISION NOT NULL,
    y DOUBLE PRECISION NOT NULL,
    geom geometry(Point, 0) NOT NULL
) ON COMMIT DROP
""".strip()
        )
        cursor.execute(
            f"""
CREATE TEMP TABLE {search_table} (
    id BIGINT NOT NULL,
    x DOUBLE PRECISION NOT NULL,
    y DOUBLE PRECISION NOT NULL,
    geom geometry(Point, 0) NOT NULL
) ON COMMIT DROP
""".strip()
        )
        cursor.executemany(
            f"""
INSERT INTO {query_table} (id, x, y, geom)
VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 0))
""".strip(),
            [(point.id, point.x, point.y, point.x, point.y) for point in query_points],
        )
        cursor.executemany(
            f"""
INSERT INTO {search_table} (id, x, y, geom)
VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 0))
""".strip(),
            [(point.id, point.x, point.y, point.x, point.y) for point in search_points],
        )
        cursor.execute(
            f"CREATE INDEX {query_table}_geom_gist ON {query_table} USING GIST (geom)"
        )
        cursor.execute(
            f"CREATE INDEX {search_table}_geom_gist ON {search_table} USING GIST (geom)"
        )
        cursor.execute(f"ANALYZE {query_table}")
        cursor.execute(f"ANALYZE {search_table}")
    finally:
        cursor.close()


def prepare_postgis_point3d_tables(
    connection,
    query_points: tuple[Point3D, ...],
    search_points: tuple[Point3D, ...],
    *,
    query_table: str = "rtdl_query_points3d_tmp",
    search_table: str = "rtdl_search_points3d_tmp",
) -> None:
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"""
CREATE TEMP TABLE {query_table} (
    id BIGINT NOT NULL,
    x DOUBLE PRECISION NOT NULL,
    y DOUBLE PRECISION NOT NULL,
    z DOUBLE PRECISION NOT NULL,
    geom geometry(PointZ, 0) NOT NULL
) ON COMMIT DROP
""".strip()
        )
        cursor.execute(
            f"""
CREATE TEMP TABLE {search_table} (
    id BIGINT NOT NULL,
    x DOUBLE PRECISION NOT NULL,
    y DOUBLE PRECISION NOT NULL,
    z DOUBLE PRECISION NOT NULL,
    geom geometry(PointZ, 0) NOT NULL
) ON COMMIT DROP
""".strip()
        )
        cursor.executemany(
            f"""
INSERT INTO {query_table} (id, x, y, z, geom)
VALUES (%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s, %s), 0))
""".strip(),
            [(point.id, point.x, point.y, point.z, point.x, point.y, point.z) for point in query_points],
        )
        cursor.executemany(
            f"""
INSERT INTO {search_table} (id, x, y, z, geom)
VALUES (%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s, %s), 0))
""".strip(),
            [(point.id, point.x, point.y, point.z, point.x, point.y, point.z) for point in search_points],
        )
        cursor.execute(
            f"CREATE INDEX {query_table}_geom_gist ON {query_table} USING GIST (geom gist_geometry_ops_nd)"
        )
        cursor.execute(
            f"CREATE INDEX {search_table}_geom_gist ON {search_table} USING GIST (geom gist_geometry_ops_nd)"
        )
        cursor.execute(f"ANALYZE {query_table}")
        cursor.execute(f"ANALYZE {search_table}")
    finally:
        cursor.close()


def query_postgis_fixed_radius_neighbors(
    connection,
    *,
    radius: float,
    k_max: int,
    query_table: str = "rtdl_query_points_tmp",
    search_table: str = "rtdl_search_points_tmp",
) -> tuple[dict[str, float | int], ...]:
    cursor = connection.cursor()
    try:
        cursor.execute(
            build_postgis_fixed_radius_neighbors_sql(
                query_table=query_table,
                search_table=search_table,
            ),
            (radius, k_max),
        )
        rows = cursor.fetchall()
        return tuple(
            {
                "query_id": int(query_id),
                "neighbor_id": int(neighbor_id),
                "distance": float(distance),
            }
            for query_id, neighbor_id, distance in rows
        )
    finally:
        cursor.close()


def run_postgis_knn_rows(
    connection,
    query_points: tuple[Point, ...],
    search_points: tuple[Point, ...],
    *,
    k: int,
    query_table: str = "rtdl_query_points_tmp",
    search_table: str = "rtdl_search_points_tmp",
) -> tuple[dict[str, float | int], ...]:
    prepare_postgis_point_tables(
        connection,
        query_points,
        search_points,
        query_table=query_table,
        search_table=search_table,
    )
    return query_postgis_knn_rows(
        connection,
        k=k,
        query_table=query_table,
        search_table=search_table,
    )


def query_postgis_knn_rows(
    connection,
    *,
    k: int,
    query_table: str = "rtdl_query_points_tmp",
    search_table: str = "rtdl_search_points_tmp",
) -> tuple[dict[str, float | int], ...]:
    cursor = connection.cursor()
    try:
        cursor.execute(
            build_postgis_knn_rows_sql(
                query_table=query_table,
                search_table=search_table,
            ),
            (k,),
        )
        rows = cursor.fetchall()
        return tuple(
            {
                "query_id": int(query_id),
                "neighbor_id": int(neighbor_id),
                "distance": float(distance),
                "neighbor_rank": int(neighbor_rank),
            }
            for query_id, neighbor_id, distance, neighbor_rank in rows
        )
    finally:
        cursor.close()


def run_postgis_knn_rows_3d(
    connection,
    query_points: tuple[Point3D, ...],
    search_points: tuple[Point3D, ...],
    *,
    k: int,
    query_table: str = "rtdl_query_points3d_tmp",
    search_table: str = "rtdl_search_points3d_tmp",
) -> tuple[dict[str, float | int], ...]:
    prepare_postgis_point3d_tables(
        connection,
        query_points,
        search_points,
        query_table=query_table,
        search_table=search_table,
    )
    return query_postgis_knn_rows_3d(
        connection,
        k=k,
        query_table=query_table,
        search_table=search_table,
    )


def query_postgis_knn_rows_3d(
    connection,
    *,
    k: int,
    query_table: str = "rtdl_query_points3d_tmp",
    search_table: str = "rtdl_search_points3d_tmp",
) -> tuple[dict[str, float | int], ...]:
    cursor = connection.cursor()
    try:
        cursor.execute(
            build_postgis_knn_rows_3d_sql(
                query_table=query_table,
                search_table=search_table,
            ),
            (k,),
        )
        rows = cursor.fetchall()
        return tuple(
            {
                "query_id": int(query_id),
                "neighbor_id": int(neighbor_id),
                "distance": float(distance),
                "neighbor_rank": int(neighbor_rank),
            }
            for query_id, neighbor_id, distance, neighbor_rank in rows
        )
    finally:
        cursor.close()


def run_postgis_fixed_radius_neighbors_3d(
    connection,
    query_points: tuple[Point3D, ...],
    search_points: tuple[Point3D, ...],
    *,
    radius: float,
    k_max: int,
    query_table: str = "rtdl_query_points3d_tmp",
    search_table: str = "rtdl_search_points3d_tmp",
) -> tuple[dict[str, float | int], ...]:
    prepare_postgis_point3d_tables(
        connection,
        query_points,
        search_points,
        query_table=query_table,
        search_table=search_table,
    )
    return query_postgis_fixed_radius_neighbors_3d(
        connection,
        radius=radius,
        k_max=k_max,
        query_table=query_table,
        search_table=search_table,
    )


def query_postgis_fixed_radius_neighbors_3d(
    connection,
    *,
    radius: float,
    k_max: int,
    query_table: str = "rtdl_query_points3d_tmp",
    search_table: str = "rtdl_search_points3d_tmp",
) -> tuple[dict[str, float | int], ...]:
    cursor = connection.cursor()
    try:
        cursor.execute(
            build_postgis_fixed_radius_neighbors_3d_sql(
                query_table=query_table,
                search_table=search_table,
            ),
            (radius, k_max),
        )
        rows = cursor.fetchall()
        return tuple(
            {
                "query_id": int(query_id),
                "neighbor_id": int(neighbor_id),
                "distance": float(distance),
            }
            for query_id, neighbor_id, distance in rows
        )
    finally:
        cursor.close()


def run_postgis_bounded_knn_rows_3d(
    connection,
    query_points: tuple[Point3D, ...],
    search_points: tuple[Point3D, ...],
    *,
    radius: float,
    k_max: int,
    query_table: str = "rtdl_query_points3d_tmp",
    search_table: str = "rtdl_search_points3d_tmp",
) -> tuple[dict[str, float | int], ...]:
    prepare_postgis_point3d_tables(
        connection,
        query_points,
        search_points,
        query_table=query_table,
        search_table=search_table,
    )
    return query_postgis_bounded_knn_rows_3d(
        connection,
        radius=radius,
        k_max=k_max,
        query_table=query_table,
        search_table=search_table,
    )


def query_postgis_bounded_knn_rows_3d(
    connection,
    *,
    radius: float,
    k_max: int,
    query_table: str = "rtdl_query_points3d_tmp",
    search_table: str = "rtdl_search_points3d_tmp",
) -> tuple[dict[str, float | int], ...]:
    cursor = connection.cursor()
    try:
        cursor.execute(
            build_postgis_bounded_knn_rows_3d_sql(
                query_table=query_table,
                search_table=search_table,
            ),
            (radius, k_max),
        )
        rows = cursor.fetchall()
        return tuple(
            {
                "query_id": int(query_id),
                "neighbor_id": int(neighbor_id),
                "distance": float(distance),
                "neighbor_rank": int(neighbor_rank),
            }
            for query_id, neighbor_id, distance, neighbor_rank in rows
        )
    finally:
        cursor.close()
