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
class Ray2D:
    id: int
    ox: float
    oy: float
    dx: float
    dy: float
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
    rays: tuple[Ray2D, ...],
    triangles: tuple[Triangle, ...],
) -> tuple[dict[str, int], ...]:
    results = []
    for ray in rays:
        hit_count = 0
        for triangle in triangles:
            if _finite_ray_hits_triangle(ray, triangle):
                hit_count += 1
        results.append({"ray_id": ray.id, "hit_count": hit_count})
    return tuple(results)


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


def _finite_ray_hits_triangle(ray: Ray2D, triangle: Triangle) -> bool:
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
