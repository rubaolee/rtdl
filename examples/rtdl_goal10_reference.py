from __future__ import annotations

import rtdsl as rt


@rt.kernel(backend="rayjoin", precision="float_approx")
def segment_polygon_hitcount_reference():
    segments = rt.input("segments", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(segments, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_hitcount(exact=False))
    return rt.emit(hits, fields=["segment_id", "hit_count"])


@rt.kernel(backend="rayjoin", precision="float_approx")
def point_nearest_segment_reference():
    points = rt.input("points", rt.Points, layout=rt.Point2DLayout, role="probe")
    segments = rt.input("segments", rt.Segments, layout=rt.Segment2DLayout, role="build")
    candidates = rt.traverse(points, segments, accel="bvh")
    nearest = rt.refine(candidates, predicate=rt.point_nearest_segment(exact=False))
    return rt.emit(nearest, fields=["point_id", "segment_id", "distance"])


def make_segment_polygon_authored_case():
    segments = (
        rt.Segment(id=1, x0=-1.0, y0=1.0, x1=3.0, y1=1.0),
        rt.Segment(id=2, x0=5.0, y0=5.0, x1=6.0, y1=6.0),
    )
    polygons = (
        rt.Polygon(id=10, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),
        rt.Polygon(id=11, vertices=((4.0, 4.0), (7.0, 4.0), (7.0, 7.0), (4.0, 7.0))),
    )
    return {"segments": segments, "polygons": polygons}


def make_point_nearest_segment_authored_case():
    points = (
        rt.Point(id=100, x=0.5, y=0.5),
        rt.Point(id=101, x=3.5, y=1.0),
    )
    segments = (
        rt.Segment(id=1, x0=0.0, y0=0.0, x1=0.0, y1=2.0),
        rt.Segment(id=2, x0=4.0, y0=0.0, x1=4.0, y1=2.0),
    )
    return {"points": points, "segments": segments}


def make_fixture_segment_polygon_case():
    county = rt.load_cdb("tests/fixtures/rayjoin/br_county_subset.cdb")
    segments = tuple(rt.Segment(**{k: v for k, v in record.items() if k in {"id", "x0", "y0", "x1", "y1"}}) for record in rt.chains_to_segments(county)[:10])
    polygons = (
        rt.Polygon(id=chain.chain_id, vertices=tuple((point.x, point.y) for point in chain.points))
        for chain in county.chains[:2]
        if len(chain.points) >= 3
    )
    return {"segments": segments, "polygons": tuple(polygons)}


def make_fixture_point_nearest_segment_case():
    county = rt.load_cdb("tests/fixtures/rayjoin/br_county_subset.cdb")
    points = tuple(rt.Point(id=record["id"], x=record["x"], y=record["y"]) for record in rt.chains_to_probe_points(county))
    segments = tuple(rt.Segment(**{k: v for k, v in record.items() if k in {"id", "x0", "y0", "x1", "y1"}}) for record in rt.chains_to_segments(county)[:12])
    return {"points": points, "segments": segments}


GOAL10_KERNELS = (
    segment_polygon_hitcount_reference,
    point_nearest_segment_reference,
)
