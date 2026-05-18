from __future__ import annotations

from .api import bounded_knn_rows as _bounded_knn_rows
from .api import compile_kernel
from .api import emit
from .api import fixed_radius_neighbors as _fixed_radius_neighbors
from .api import grouped_count
from .api import grouped_sum
from .api import input
from .api import kernel
from .api import knn_rows as _knn_rows
from .api import polygon_pair_overlap_area_rows as _polygon_pair_overlap_area_rows
from .api import polygon_set_jaccard as _polygon_set_jaccard
from .api import ray_triangle_any_hit as _ray_triangle_any_hit
from .api import ray_triangle_closest_hit as _ray_triangle_closest_hit
from .api import ray_triangle_hit_count as _ray_triangle_hit_count
from .api import refine
from .api import segment_intersection as _segment_intersection
from .api import segment_polygon_anyhit_rows as _segment_polygon_anyhit_rows
from .api import segment_polygon_hitcount as _segment_polygon_hitcount
from .api import traverse


def any_hit(*, exact: bool = False):
    """Generic any-hit predicate over the current ray/primitive contract."""
    return _ray_triangle_any_hit(exact=exact)


def hit_count(*, exact: bool = False):
    """Generic hit-count predicate over the current ray/primitive contract."""
    return _ray_triangle_hit_count(exact=exact)


def closest_hit(*, exact: bool = False):
    """Generic closest-hit predicate over the current ray/primitive contract."""
    return _ray_triangle_closest_hit(exact=exact)


def intersections(*, exact: bool = False):
    """Generic segment intersection predicate."""
    return _segment_intersection(exact=exact)


def shape_hit_count(*, exact: bool = False):
    """Generic segment/shape hit-count predicate."""
    return _segment_polygon_hitcount(exact=exact)


def shape_any_hit_rows(*, exact: bool = False):
    """Generic segment/shape witness-row predicate."""
    return _segment_polygon_anyhit_rows(exact=exact)


def shape_pair_overlap_rows(*, exact: bool = False):
    """Generic shape-pair overlap summary predicate."""
    return _polygon_pair_overlap_area_rows(exact=exact)


def shape_set_similarity(*, exact: bool = False):
    """Generic shape-set similarity predicate."""
    return _polygon_set_jaccard(exact=exact)


def nearest(*, k: int):
    """Generic K-nearest row predicate."""
    return _knn_rows(k=k)


def bounded_nearest(*, radius: float, k_max: int):
    """Generic bounded nearest-neighbor row predicate."""
    return _bounded_knn_rows(radius=radius, k_max=k_max)


def within_radius(*, radius: float, k_max: int):
    """Generic fixed-radius neighbor predicate."""
    return _fixed_radius_neighbors(radius=radius, k_max=k_max)


__all__ = [
    "any_hit",
    "bounded_nearest",
    "closest_hit",
    "compile_kernel",
    "emit",
    "grouped_count",
    "grouped_sum",
    "hit_count",
    "input",
    "intersections",
    "kernel",
    "nearest",
    "refine",
    "shape_any_hit_rows",
    "shape_hit_count",
    "shape_pair_overlap_rows",
    "shape_set_similarity",
    "traverse",
    "within_radius",
]
