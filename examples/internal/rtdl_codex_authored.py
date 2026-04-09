import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def road_boundary_crossings():
    roads = rt.input("roads", rt.Segments, role="probe")
    boundaries = rt.input("boundaries", rt.Segments, role="build")
    candidates = rt.traverse(roads, boundaries, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(
        hits,
        fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
    )


@rt.kernel(backend="rtdl", precision="float_approx")
def station_in_districts():
    stations = rt.input("stations", rt.Points, role="probe")
    districts = rt.input("districts", rt.Polygons, role="build")
    candidates = rt.traverse(stations, districts, accel="bvh")
    hits = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(exact=False, boundary_mode="inclusive"),
    )
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


@rt.kernel(backend="rtdl", precision="float_approx")
def parcel_flood_overlay():
    parcels = rt.input("parcels", rt.Polygons, role="probe")
    floodzones = rt.input("floodzones", rt.Polygons, role="build")
    candidates = rt.traverse(parcels, floodzones, accel="bvh")
    seeds = rt.refine(candidates, predicate=rt.overlay_compose())
    return rt.emit(
        seeds,
        fields=["left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"],
    )


CODEX_AUTHORED_KERNELS = (
    road_boundary_crossings,
    station_in_districts,
    parcel_flood_overlay,
)
