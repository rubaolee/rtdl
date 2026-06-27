from __future__ import annotations

from pathlib import Path

import rtdsl as rt
from rtdsl.datasets import chains_to_probe_points
from rtdsl.datasets import load_cdb
from rtdsl.datasets import load_natural_earth_populated_places_geojson
from rtdsl.reference import Point

ROOT = Path(__file__).resolve().parents[2]


@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_neighbors_reference():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=0.5, k_max=3))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


def make_fixed_radius_neighbors_authored_case() -> dict[str, tuple[Point, ...]]:
    return {
        "query_points": (
            Point(id=100, x=0.0, y=0.0),
            Point(id=101, x=3.0, y=0.0),
        ),
        "search_points": (
            Point(id=1, x=0.0, y=0.0),
            Point(id=2, x=0.3, y=0.0),
            Point(id=3, x=-0.3, y=0.0),
            Point(id=4, x=3.2, y=0.0),
            Point(id=5, x=4.0, y=0.0),
        ),
    }


def make_fixture_fixed_radius_neighbors_case() -> dict[str, tuple[Point, ...]]:
    county = load_cdb(ROOT / "tests" / "fixtures" / "rayjoin" / "br_county_subset.cdb")
    points = chains_to_probe_points(county, limit_chains=16)
    return {
        "query_points": tuple(points[:8]),
        "search_points": tuple(points[:16]),
    }


def make_natural_earth_fixed_radius_neighbors_case() -> dict[str, tuple[Point, ...]]:
    points = load_natural_earth_populated_places_geojson(
        ROOT / "tests" / "fixtures" / "public" / "natural_earth_populated_places_sample.geojson"
    )
    return {
        "query_points": tuple(points[:2]),
        "search_points": tuple(points),
    }
