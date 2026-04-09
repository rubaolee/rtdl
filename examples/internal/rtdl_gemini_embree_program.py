import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def gemini_embree_polygon_test():
    points = rt.input("points", rt.Points, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(exact=False, boundary_mode="inclusive"),
    )
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


GEMINI_EMBREE_KERNELS = (gemini_embree_polygon_test,)


def run_demo():
    points_data = [{"id": 0, "x": 0.5, "y": 0.5}, {"id": 1, "x": 1.5, "y": 1.5}]
    polygons_data = [
        {"id": 10, "vertices": [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]}
    ]

    result = rt.run_embree(
        gemini_embree_polygon_test,
        points=points_data,
        polygons=polygons_data,
    )
    return result


if __name__ == "__main__":
    print(run_demo())
