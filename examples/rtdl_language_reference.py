import rtdsl as rt


@rt.kernel(backend="rayjoin", precision="float_approx")
def county_zip_join_reference():
    left = rt.input("left", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    right = rt.input("right", rt.Segments, layout=rt.Segment2DLayout, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(
        hits,
        fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
    )


@rt.kernel(backend="rayjoin", precision="float_approx")
def point_in_counties_reference():
    points = rt.input("points", rt.Points, layout=rt.Point2DLayout, role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(exact=False, boundary_mode="inclusive"),
    )
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


@rt.kernel(backend="rayjoin", precision="float_approx")
def county_soil_overlay_reference():
    left = rt.input("left", rt.Polygons, layout=rt.Polygon2DLayout, role="probe")
    right = rt.input("right", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    seeds = rt.refine(candidates, predicate=rt.overlay_compose())
    return rt.emit(
        seeds,
        fields=["left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"],
    )


LANGUAGE_REFERENCE_KERNELS = (
    county_zip_join_reference,
    point_in_counties_reference,
    county_soil_overlay_reference,
)
