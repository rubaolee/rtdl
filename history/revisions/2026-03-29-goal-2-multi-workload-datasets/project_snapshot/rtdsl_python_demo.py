from pathlib import Path

import rtdsl as rt


def segment_layout():
    return rt.layout(
        "Segment2D",
        rt.field("x0", rt.f32),
        rt.field("y0", rt.f32),
        rt.field("x1", rt.f32),
        rt.field("y1", rt.f32),
        rt.field("id", rt.u32),
    )


def point_layout():
    return rt.layout(
        "Point2D",
        rt.field("x", rt.f32),
        rt.field("y", rt.f32),
        rt.field("id", rt.u32),
    )


def polygon_layout():
    return rt.layout(
        "Polygon2DRef",
        rt.field("vertex_offset", rt.u32),
        rt.field("vertex_count", rt.u32),
        rt.field("id", rt.u32),
    )


@rt.kernel(backend="rayjoin", precision="float_approx")
def county_zip_join():
    left = rt.input("left", rt.Segments, layout=segment_layout(), role="probe")
    right = rt.input("right", rt.Segments, layout=segment_layout(), role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(
        hits,
        fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
    )


@rt.kernel(backend="rayjoin", precision="float_approx")
def point_in_counties():
    points = rt.input("points", rt.Points, layout=point_layout(), role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=polygon_layout(), role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.point_in_polygon(exact=False))
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


@rt.kernel(backend="rayjoin", precision="float_approx")
def county_soil_overlay():
    left = rt.input("left", rt.Polygons, layout=polygon_layout(), role="probe")
    right = rt.input("right", rt.Polygons, layout=polygon_layout(), role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    seeds = rt.refine(candidates, predicate=rt.overlay_compose())
    return rt.emit(
        seeds,
        fields=["left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"],
    )


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    for kernel in (county_zip_join, point_in_counties, county_soil_overlay):
        compiled = rt.compile_kernel(kernel)
        plan = rt.lower_to_rayjoin(compiled)
        generated = rt.generate_optix_project(plan, root / "generated" / compiled.name)

        print(compiled.format())
        print()
        print(plan.format())
        print()
        print("Generated Files")
        print("---------------")
        for label, path in generated.items():
            print(f"{label:8}: {path}")
        print()

    county = rt.load_cdb(root / "tests" / "fixtures" / "rayjoin" / "br_county_subset.cdb")
    soil = rt.load_cdb(root / "tests" / "fixtures" / "rayjoin" / "br_soil_subset.cdb")
    print("RayJoin Sample Fixtures")
    print("----------------------")
    print(f"county chains  : {len(county.chains)}")
    print(f"county segments: {len(rt.chains_to_segments(county))}")
    print(f"soil chains    : {len(soil.chains)}")
    print(f"soil points    : {len(rt.chains_to_probe_points(soil))}")
    print(f"county faces   : {len(rt.chains_to_polygon_refs(county))}")
    print(f"soil faces     : {len(rt.chains_to_polygon_refs(soil))}")


if __name__ == "__main__":
    main()
