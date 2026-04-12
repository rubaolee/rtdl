from __future__ import annotations

from dataclasses import dataclass

from .reference import Point3D


@dataclass(frozen=True)
class ExactCrossPackageMatch:
    query_id: int
    search_id: int
    x: float
    y: float
    z: float


def find_exact_cross_package_matches(
    query_points: tuple[Point3D, ...],
    search_points: tuple[Point3D, ...],
) -> tuple[ExactCrossPackageMatch, ...]:
    search_by_xyz: dict[tuple[float, float, float], list[Point3D]] = {}
    for search_point in search_points:
        key = (search_point.x, search_point.y, search_point.z)
        search_by_xyz.setdefault(key, []).append(search_point)

    matches: list[ExactCrossPackageMatch] = []
    for query_point in query_points:
        key = (query_point.x, query_point.y, query_point.z)
        for search_point in search_by_xyz.get(key, ()):
            matches.append(
                ExactCrossPackageMatch(
                    query_id=query_point.id,
                    search_id=search_point.id,
                    x=query_point.x,
                    y=query_point.y,
                    z=query_point.z,
                )
            )
    matches.sort(key=lambda item: (item.query_id, item.search_id))
    return tuple(matches)
