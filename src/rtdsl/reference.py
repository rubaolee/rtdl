from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Segment:
    id: int
    x0: float
    y0: float
    x1: float
    y1: float


@dataclass(frozen=True)
class Point:
    id: int
    x: float
    y: float


@dataclass(frozen=True)
class Point3D:
    id: int
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Polygon:
    id: int
    vertices: tuple[tuple[float, float], ...]


@dataclass(frozen=True)
class Triangle:
    id: int
    x0: float
    y0: float
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(frozen=True)
class Triangle3D:
    id: int
    x0: float
    y0: float
    z0: float
    x1: float
    y1: float
    z1: float
    x2: float
    y2: float
    z2: float


@dataclass(frozen=True)
class Ray2D:
    id: int
    ox: float
    oy: float
    dx: float
    dy: float
    tmax: float


@dataclass(frozen=True)
class Ray3D:
    id: int
    ox: float
    oy: float
    oz: float
    dx: float
    dy: float
    dz: float
    tmax: float


def lsi_cpu(left: tuple[Segment, ...], right: tuple[Segment, ...]) -> tuple[dict[str, float | int], ...]:
    hits = []
    for left_seg in left:
        for right_seg in right:
            result = _segment_intersection(left_seg, right_seg)
            if result is None:
                continue
            ix, iy = result
            hits.append(
                {
                    "left_id": left_seg.id,
                    "right_id": right_seg.id,
                    "intersection_point_x": ix,
                    "intersection_point_y": iy,
                }
            )
    return tuple(hits)


def pip_cpu(
    points: tuple[Point, ...],
    polygons: tuple[Polygon, ...],
    *,
    boundary_mode: str = "inclusive",
    result_mode: str = "full_matrix",
) -> tuple[dict[str, int], ...]:
    if result_mode not in {"full_matrix", "positive_hits"}:
        raise ValueError("pip_cpu result_mode must be 'full_matrix' or 'positive_hits'")
    results = []
    bounds = None
    if result_mode == "positive_hits":
        bounds = []
        for polygon in polygons:
            xs = [vx for vx, _ in polygon.vertices]
            ys = [vy for _, vy in polygon.vertices]
            bounds.append((min(xs), min(ys), max(xs), max(ys)))
    for point in points:
        for polygon_index, polygon in enumerate(polygons):
            if bounds is not None:
                min_x, min_y, max_x, max_y = bounds[polygon_index]
                if point.x < min_x or point.x > max_x or point.y < min_y or point.y > max_y:
                    continue
            contains = 1 if _point_in_polygon(point.x, point.y, polygon.vertices, boundary_mode=boundary_mode) else 0
            if result_mode == "positive_hits" and contains != 1:
                continue
            results.append({"point_id": point.id, "polygon_id": polygon.id, "contains": contains})
    return tuple(results)


def overlay_compose_cpu(
    left_polygons: tuple[Polygon, ...],
    right_polygons: tuple[Polygon, ...],
) -> tuple[dict[str, int], ...]:
    left_segments = _segments_from_polygons(left_polygons)
    right_segments = _segments_from_polygons(right_polygons)
    lsi_hits = lsi_cpu(left_segments, right_segments)

    left_points = tuple(Point(id=polygon.id, x=polygon.vertices[0][0], y=polygon.vertices[0][1]) for polygon in left_polygons)
    right_points = tuple(Point(id=polygon.id, x=polygon.vertices[0][0], y=polygon.vertices[0][1]) for polygon in right_polygons)
    left_in_right = pip_cpu(left_points, right_polygons, boundary_mode="inclusive")
    right_in_left = pip_cpu(right_points, left_polygons, boundary_mode="inclusive")

    results = []
    for left_polygon in left_polygons:
        for right_polygon in right_polygons:
            requires_lsi = 1 if any(hit["left_id"] == left_polygon.id and hit["right_id"] == right_polygon.id for hit in lsi_hits) else 0
            requires_pip = 1 if any(
                (hit["point_id"] == left_polygon.id and hit["polygon_id"] == right_polygon.id and hit["contains"] == 1)
                or (hit["point_id"] == right_polygon.id and hit["polygon_id"] == left_polygon.id and hit["contains"] == 1)
                for hit in (*left_in_right, *right_in_left)
            ) else 0
            results.append(
                {
                    "left_polygon_id": left_polygon.id,
                    "right_polygon_id": right_polygon.id,
                    "requires_lsi": requires_lsi,
                    "requires_pip": requires_pip,
                }
            )
    return tuple(results)


def ray_triangle_hit_count_cpu(
    rays: tuple[Ray2D | Ray3D, ...],
    triangles: tuple[Triangle | Triangle3D, ...],
) -> tuple[dict[str, int], ...]:
    results = []
    for ray in rays:
        hit_count = 0
        for triangle in triangles:
            if _finite_ray_hits_triangle(ray, triangle):
                hit_count += 1
        results.append({"ray_id": ray.id, "hit_count": hit_count})
    return tuple(results)


def ray_triangle_closest_hit_cpu(
    rays: tuple[Ray2D | Ray3D, ...],
    triangles: tuple[Triangle | Triangle3D, ...],
) -> tuple[dict[str, float | int], ...]:
    results = []
    for ray in rays:
        best_t: float | None = None
        best_triangle_id: int | None = None
        for triangle in triangles:
            hit_t = _finite_ray_triangle_hit_t(ray, triangle)
            if hit_t is None:
                continue
            triangle_id = int(triangle.id)
            if best_t is None or hit_t < best_t or (hit_t == best_t and triangle_id < int(best_triangle_id)):
                best_t = hit_t
                best_triangle_id = triangle_id
        if best_t is not None and best_triangle_id is not None:
            results.append({"ray_id": int(ray.id), "triangle_id": best_triangle_id, "t": best_t})
    return tuple(results)


def fixed_radius_neighbors_cpu(
    query_points: tuple[Point | Point3D, ...],
    search_points: tuple[Point | Point3D, ...],
    *,
    radius: float,
    k_max: int,
) -> tuple[dict[str, float | int], ...]:
    rows = []
    radius_sq = radius * radius
    for query_point in query_points:
        candidates = []
        for search_point in search_points:
            distance_sq = _point_distance_sq(query_point, search_point)
            if distance_sq > radius_sq:
                continue
            candidates.append((math.sqrt(distance_sq), search_point.id))

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


def knn_rows_cpu(
    query_points: tuple[Point | Point3D, ...],
    search_points: tuple[Point | Point3D, ...],
    *,
    k: int,
) -> tuple[dict[str, float | int], ...]:
    rows = []
    for query_point in query_points:
        candidates = []
        for search_point in search_points:
            distance = math.sqrt(_point_distance_sq(query_point, search_point))
            candidates.append((distance, search_point.id))

        candidates.sort(key=lambda item: (item[0], item[1]))
        for rank, (distance, neighbor_id) in enumerate(candidates[:k], start=1):
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


def bounded_knn_rows_cpu(
    query_points: tuple[Point | Point3D, ...],
    search_points: tuple[Point | Point3D, ...],
    *,
    radius: float,
    k_max: int,
) -> tuple[dict[str, float | int], ...]:
    rows = []
    radius_sq = radius * radius
    for query_point in query_points:
        candidates = []
        for search_point in search_points:
            distance_sq = _point_distance_sq(query_point, search_point)
            if distance_sq > radius_sq:
                continue
            candidates.append((math.sqrt(distance_sq), search_point.id))

        candidates.sort(key=lambda item: (item[0], item[1]))
        for rank, (distance, neighbor_id) in enumerate(candidates[:k_max], start=1):
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


def segment_polygon_hitcount_cpu(
    segments: tuple[Segment, ...],
    polygons: tuple[Polygon, ...],
) -> tuple[dict[str, int], ...]:
    polygon_bounds = tuple(_polygon_bounds(polygon) for polygon in polygons)
    bucket_index = _build_polygon_bucket_index(polygon_bounds)
    rows = []
    for segment in segments:
        seg_bounds = _segment_bounds(segment)
        hit_count = 0
        for polygon_index in _candidate_polygon_indexes(seg_bounds, polygon_bounds, bucket_index):
            polygon = polygons[polygon_index]
            poly_bounds = polygon_bounds[polygon_index]
            if not _bounds_overlap(seg_bounds, poly_bounds):
                continue
            if _segment_hits_polygon(segment, polygon):
                hit_count += 1
        rows.append({"segment_id": segment.id, "hit_count": hit_count})
    return tuple(rows)


def segment_polygon_anyhit_rows_cpu(
    segments: tuple[Segment, ...],
    polygons: tuple[Polygon, ...],
) -> tuple[dict[str, int], ...]:
    polygon_bounds = tuple(_polygon_bounds(polygon) for polygon in polygons)
    bucket_index = _build_polygon_bucket_index(polygon_bounds)
    rows = []
    for segment in segments:
        seg_bounds = _segment_bounds(segment)
        for polygon_index in _candidate_polygon_indexes(seg_bounds, polygon_bounds, bucket_index):
            polygon = polygons[polygon_index]
            poly_bounds = polygon_bounds[polygon_index]
            if not _bounds_overlap(seg_bounds, poly_bounds):
                continue
            if _segment_hits_polygon(segment, polygon):
                rows.append({"segment_id": segment.id, "polygon_id": polygon.id})
    return tuple(rows)


def polygon_pair_overlap_area_rows_cpu(
    left_polygons: tuple[Polygon, ...],
    right_polygons: tuple[Polygon, ...],
) -> tuple[dict[str, int], ...]:
    left_bounds = tuple(_polygon_bounds(polygon) for polygon in left_polygons)
    right_bounds = tuple(_polygon_bounds(polygon) for polygon in right_polygons)
    right_bucket_index = _build_polygon_bucket_index(right_bounds)
    right_cell_sets = tuple(_polygon_unit_cells(polygon) for polygon in right_polygons)
    right_areas = tuple(len(cells) for cells in right_cell_sets)

    rows = []
    for left_index, left_polygon in enumerate(left_polygons):
        left_cells = _polygon_unit_cells(left_polygon)
        left_area = len(left_cells)
        left_bounds_row = left_bounds[left_index]
        left_cell_lookup = set(left_cells)
        for right_index in _candidate_polygon_indexes(left_bounds_row, right_bounds, right_bucket_index):
            if not _bounds_overlap(left_bounds_row, right_bounds[right_index]):
                continue
            intersection_area = sum(1 for cell in right_cell_sets[right_index] if cell in left_cell_lookup)
            if intersection_area <= 0:
                continue
            right_polygon = right_polygons[right_index]
            right_area = right_areas[right_index]
            rows.append(
                {
                    "left_polygon_id": left_polygon.id,
                    "right_polygon_id": right_polygon.id,
                    "intersection_area": intersection_area,
                    "left_area": left_area,
                    "right_area": right_area,
                    "union_area": left_area + right_area - intersection_area,
                }
            )
    return tuple(rows)


def polygon_set_jaccard_cpu(
    left_polygons: tuple[Polygon, ...],
    right_polygons: tuple[Polygon, ...],
) -> tuple[dict[str, float | int], ...]:
    left_cells = _polygon_set_unit_cells(left_polygons)
    right_cells = _polygon_set_unit_cells(right_polygons)
    intersection_area = len(left_cells & right_cells)
    left_area = len(left_cells)
    right_area = len(right_cells)
    union_area = len(left_cells | right_cells)
    jaccard_similarity = 0.0 if union_area == 0 else intersection_area / union_area
    return (
        {
            "intersection_area": intersection_area,
            "left_area": left_area,
            "right_area": right_area,
            "union_area": union_area,
            "jaccard_similarity": jaccard_similarity,
        },
    )


def point_nearest_segment_cpu(
    points: tuple[Point, ...],
    segments: tuple[Segment, ...],
) -> tuple[dict[str, float | int], ...]:
    rows = []
    for point in points:
        best_segment = None
        best_distance = None
        for segment in segments:
            distance = _point_segment_distance(point, segment)
            if (
                best_distance is None
                or distance < best_distance - 1.0e-7
                or (abs(distance - best_distance) <= 1.0e-7 and segment.id < best_segment.id)
            ):
                best_segment = segment
                best_distance = distance
        if best_segment is None:
            continue
        rows.append(
            {
                "point_id": point.id,
                "segment_id": best_segment.id,
                "distance": best_distance,
            }
        )
    return tuple(rows)


def _segments_from_polygons(polygons: tuple[Polygon, ...]) -> tuple[Segment, ...]:
    segments = []
    for polygon in polygons:
        vertices = list(polygon.vertices)
        wrapped = vertices + [vertices[0]]
        for start, end in zip(wrapped, wrapped[1:]):
            segments.append(Segment(id=polygon.id, x0=start[0], y0=start[1], x1=end[0], y1=end[1]))
    return tuple(segments)


def _segment_bounds(segment: Segment) -> tuple[float, float, float, float]:
    return (
        min(segment.x0, segment.x1),
        min(segment.y0, segment.y1),
        max(segment.x0, segment.x1),
        max(segment.y0, segment.y1),
    )


def _polygon_bounds(polygon: Polygon) -> tuple[float, float, float, float]:
    xs = [vx for vx, _ in polygon.vertices]
    ys = [vy for _, vy in polygon.vertices]
    return (min(xs), min(ys), max(xs), max(ys))


def _bounds_overlap(
    left: tuple[float, float, float, float],
    right: tuple[float, float, float, float],
) -> bool:
    return not (
        left[2] < right[0]
        or right[2] < left[0]
        or left[3] < right[1]
        or right[3] < left[1]
    )


def _build_polygon_bucket_index(
    polygon_bounds: tuple[tuple[float, float, float, float], ...],
) -> dict[str, object]:
    if not polygon_bounds:
        return {"origin_x": 0.0, "bucket_width": 1.0, "buckets": tuple()}
    global_min = min(bounds[0] for bounds in polygon_bounds)
    global_max = max(bounds[2] for bounds in polygon_bounds)
    span = max(global_max - global_min, 1.0e-9)
    bucket_count = max(16, min(len(polygon_bounds) * 2, 8192))
    bucket_width = span / bucket_count
    buckets: list[list[int]] = [[] for _ in range(bucket_count)]
    for polygon_index, bounds in enumerate(polygon_bounds):
        first = max(0, min(bucket_count - 1, int(math.floor((bounds[0] - global_min) / bucket_width))))
        last = max(0, min(bucket_count - 1, int(math.floor((bounds[2] - global_min) / bucket_width))))
        for bucket_id in range(first, last + 1):
            buckets[bucket_id].append(polygon_index)
    return {
        "origin_x": global_min,
        "bucket_width": bucket_width,
        "buckets": tuple(tuple(bucket) for bucket in buckets),
    }


def _polygon_unit_cells(polygon: Polygon) -> tuple[tuple[int, int], ...]:
    _require_pathology_grid_polygon(polygon)
    min_x, min_y, max_x, max_y = _polygon_bounds(polygon)
    cells: list[tuple[int, int]] = []
    for iy in range(int(math.floor(min_y)), int(math.ceil(max_y))):
        for ix in range(int(math.floor(min_x)), int(math.ceil(max_x))):
            if _point_in_polygon(ix + 0.5, iy + 0.5, polygon.vertices):
                cells.append((ix, iy))
    return tuple(cells)


def _polygon_set_unit_cells(polygons: tuple[Polygon, ...]) -> set[tuple[int, int]]:
    cells: set[tuple[int, int]] = set()
    for polygon in polygons:
        for cell in _polygon_unit_cells(polygon):
            cells.add(cell)
    return cells


def _require_pathology_grid_polygon(polygon: Polygon) -> None:
    if len(polygon.vertices) < 3:
        raise ValueError("polygon_pair_overlap_area_rows requires polygons with at least 3 vertices")
    vertices = polygon.vertices
    for x, y in vertices:
        if not _is_close_to_integer(x) or not _is_close_to_integer(y):
            raise ValueError(
                "polygon_pair_overlap_area_rows currently requires integer-grid polygon vertices"
            )
    wrapped = vertices + (vertices[0],)
    for start, end in zip(wrapped, wrapped[1:]):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        if abs(dx) <= 1.0e-12 and abs(dy) <= 1.0e-12:
            raise ValueError("polygon_pair_overlap_area_rows does not accept zero-length polygon edges")
        if abs(dx) > 1.0e-12 and abs(dy) > 1.0e-12:
            raise ValueError(
                "polygon_pair_overlap_area_rows currently requires orthogonal integer-grid polygons"
            )


def _is_close_to_integer(value: float) -> bool:
    return abs(value - round(value)) <= 1.0e-9


def _candidate_polygon_indexes(
    seg_bounds: tuple[float, float, float, float],
    polygon_bounds: tuple[tuple[float, float, float, float], ...],
    bucket_index: dict[str, object],
) -> tuple[int, ...]:
    buckets = bucket_index["buckets"]
    if not buckets:
        return tuple()
    origin_x = float(bucket_index["origin_x"])
    bucket_width = float(bucket_index["bucket_width"])
    bucket_count = len(buckets)
    first = max(0, min(bucket_count - 1, int(math.floor((seg_bounds[0] - origin_x) / bucket_width))))
    last = max(0, min(bucket_count - 1, int(math.floor((seg_bounds[2] - origin_x) / bucket_width))))
    seen: set[int] = set()
    candidates: list[int] = []
    for bucket_id in range(first, last + 1):
        for polygon_index in buckets[bucket_id]:
            if polygon_index in seen:
                continue
            seen.add(polygon_index)
            candidates.append(polygon_index)
    return tuple(candidates)


def _segment_intersection(left: Segment, right: Segment) -> tuple[float, float] | None:
    px = left.x0
    py = left.y0
    rx = left.x1 - left.x0
    ry = left.y1 - left.y0
    qx = right.x0
    qy = right.y0
    sx = right.x1 - right.x0
    sy = right.y1 - right.y0

    denom = rx * sy - ry * sx
    if abs(denom) < 1.0e-7:
        return None

    qpx = qx - px
    qpy = qy - py
    t = (qpx * sy - qpy * sx) / denom
    u = (qpx * ry - qpy * rx) / denom
    if not (0.0 <= t <= 1.0 and 0.0 <= u <= 1.0):
        return None

    return (px + t * rx, py + t * ry)


def _point_in_polygon(
    x: float,
    y: float,
    vertices: tuple[tuple[float, float], ...],
    *,
    boundary_mode: str = "inclusive",
) -> bool:
    if boundary_mode != "inclusive":
        raise ValueError("the current point-in-polygon implementation supports only boundary_mode='inclusive'")
    point = (x, y)
    wrapped = vertices + (vertices[0],)
    for start, end in zip(wrapped, wrapped[1:]):
        if _point_on_segment(point, start, end):
            return True

    inside = False
    j = len(vertices) - 1
    for i, (xi, yi) in enumerate(vertices):
        xj, yj = vertices[j]
        on_crossing = ((yi > y) != (yj > y)) and (
            x <= (xj - xi) * (y - yi) / ((yj - yi) or 1.0e-20) + xi
        )
        if on_crossing:
            inside = not inside
        j = i
    return inside


def _point_on_segment(
    point: tuple[float, float],
    start: tuple[float, float],
    end: tuple[float, float],
) -> bool:
    eps = 1.0e-12
    px, py = point
    ax, ay = start
    bx, by = end
    length_sq = (bx - ax) ** 2 + (by - ay) ** 2
    if length_sq <= (eps ** 2):
        return abs(px - ax) <= eps and abs(py - ay) <= eps

    cross = (px - ax) * (by - ay) - (py - ay) * (bx - ax)
    length = length_sq ** 0.5
    if abs(cross) > eps * length:
        return False
    dot = (px - ax) * (bx - ax) + (py - ay) * (by - ay)
    along_eps = eps * length
    if dot < -along_eps:
        return False
    if dot - length_sq > along_eps:
        return False
    return True


def _finite_ray_hits_triangle(ray: Ray2D | Ray3D, triangle: Triangle | Triangle3D) -> bool:
    return _finite_ray_triangle_hit_t(ray, triangle) is not None


def _finite_ray_triangle_hit_t(ray: Ray2D | Ray3D, triangle: Triangle | Triangle3D) -> float | None:
    if isinstance(ray, Ray3D) or isinstance(triangle, Triangle3D):
        if not isinstance(ray, Ray3D) or not isinstance(triangle, Triangle3D):
            raise ValueError("ray_triangle_hit_count_cpu requires rays and triangles to both be 2D or both be 3D")
        return _finite_ray_triangle_hit_t_3d(ray, triangle)
    return 0.0 if _finite_ray_hits_triangle_2d(ray, triangle) else None


def _finite_ray_hits_triangle_2d(ray: Ray2D, triangle: Triangle) -> bool:
    triangle_vertices = (
        (triangle.x0, triangle.y0),
        (triangle.x1, triangle.y1),
        (triangle.x2, triangle.y2),
    )
    ex = ray.ox + ray.dx * ray.tmax
    ey = ray.oy + ray.dy * ray.tmax
    ray_segment = Segment(id=ray.id, x0=ray.ox, y0=ray.oy, x1=ex, y1=ey)

    if _point_in_triangle(ray.ox, ray.oy, triangle_vertices):
        return True
    if _point_in_triangle(ex, ey, triangle_vertices):
        return True

    triangle_edges = (
        Segment(id=triangle.id, x0=triangle.x0, y0=triangle.y0, x1=triangle.x1, y1=triangle.y1),
        Segment(id=triangle.id, x0=triangle.x1, y0=triangle.y1, x1=triangle.x2, y1=triangle.y2),
        Segment(id=triangle.id, x0=triangle.x2, y0=triangle.y2, x1=triangle.x0, y1=triangle.y0),
    )
    return any(_segment_intersection(ray_segment, edge) is not None for edge in triangle_edges)


def _finite_ray_hits_triangle_3d(ray: Ray3D, triangle: Triangle3D) -> bool:
    return _finite_ray_triangle_hit_t_3d(ray, triangle) is not None


def _finite_ray_triangle_hit_t_3d(ray: Ray3D, triangle: Triangle3D) -> float | None:
    edge1x = triangle.x1 - triangle.x0
    edge1y = triangle.y1 - triangle.y0
    edge1z = triangle.z1 - triangle.z0
    edge2x = triangle.x2 - triangle.x0
    edge2y = triangle.y2 - triangle.y0
    edge2z = triangle.z2 - triangle.z0

    pvx = ray.dy * edge2z - ray.dz * edge2y
    pvy = ray.dz * edge2x - ray.dx * edge2z
    pvz = ray.dx * edge2y - ray.dy * edge2x

    det = edge1x * pvx + edge1y * pvy + edge1z * pvz
    if abs(det) <= 1.0e-8:
        return None

    inv_det = 1.0 / det
    tvx = ray.ox - triangle.x0
    tvy = ray.oy - triangle.y0
    tvz = ray.oz - triangle.z0

    u = (tvx * pvx + tvy * pvy + tvz * pvz) * inv_det
    if u < 0.0 or u > 1.0:
        return None

    qvx = tvy * edge1z - tvz * edge1y
    qvy = tvz * edge1x - tvx * edge1z
    qvz = tvx * edge1y - tvy * edge1x

    v = (ray.dx * qvx + ray.dy * qvy + ray.dz * qvz) * inv_det
    if v < 0.0 or (u + v) > 1.0:
        return None

    t = (edge2x * qvx + edge2y * qvy + edge2z * qvz) * inv_det
    if t >= 0.0 and t <= ray.tmax:
        return t
    return None


def _segment_hits_polygon(segment: Segment, polygon: Polygon) -> bool:
    if _point_in_polygon(segment.x0, segment.y0, polygon.vertices):
        return True
    if _point_in_polygon(segment.x1, segment.y1, polygon.vertices):
        return True
    vertices = list(polygon.vertices)
    wrapped = vertices + [vertices[0]]
    for start, end in zip(wrapped, wrapped[1:]):
        edge = Segment(id=polygon.id, x0=start[0], y0=start[1], x1=end[0], y1=end[1])
        if _segment_intersection(segment, edge) is not None:
            return True
    return False


def _point_segment_distance(point: Point, segment: Segment) -> float:
    vx = segment.x1 - segment.x0
    vy = segment.y1 - segment.y0
    wx = point.x - segment.x0
    wy = point.y - segment.y0
    denom = vx * vx + vy * vy
    if denom < 1.0e-12:
        dx = point.x - segment.x0
        dy = point.y - segment.y0
        return (dx * dx + dy * dy) ** 0.5
    t = (wx * vx + wy * vy) / denom
    t = max(0.0, min(1.0, t))
    px = segment.x0 + t * vx
    py = segment.y0 + t * vy
    dx = point.x - px
    dy = point.y - py
    return (dx * dx + dy * dy) ** 0.5


def _point_distance_sq(left: Point | Point3D, right: Point | Point3D) -> float:
    # Internal helper: 2D point records are treated as z=0.0 when reused by the
    # additive 3D nearest-neighbor line.
    dx = right.x - left.x
    dy = right.y - left.y
    left_z = getattr(left, "z", 0.0)
    right_z = getattr(right, "z", 0.0)
    dz = right_z - left_z
    return dx * dx + dy * dy + dz * dz


def _point_in_triangle(x: float, y: float, vertices: tuple[tuple[float, float], ...]) -> bool:
    (ax, ay), (bx, by), (cx, cy) = vertices
    v0x = cx - ax
    v0y = cy - ay
    v1x = bx - ax
    v1y = by - ay
    v2x = x - ax
    v2y = y - ay

    dot00 = v0x * v0x + v0y * v0y
    dot01 = v0x * v1x + v0y * v1y
    dot02 = v0x * v2x + v0y * v2y
    dot11 = v1x * v1x + v1y * v1y
    dot12 = v1x * v2x + v1y * v2y

    denom = dot00 * dot11 - dot01 * dot01
    if abs(denom) < 1.0e-7:
        return False

    inv = 1.0 / denom
    u = (dot11 * dot02 - dot01 * dot12) * inv
    v = (dot00 * dot12 - dot01 * dot02) * inv
    return u >= 0.0 and v >= 0.0 and (u + v) <= 1.0
