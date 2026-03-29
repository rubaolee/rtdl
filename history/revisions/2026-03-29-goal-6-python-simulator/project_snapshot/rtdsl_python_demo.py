from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import rtdsl as rt
from examples.rtdl_ray_tri_hitcount import make_center_rays
from examples.rtdl_ray_tri_hitcount import make_random_triangles


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


@rt.kernel(backend="rayjoin", precision="float_approx")
def central_ray_triangle_stats():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


def main() -> None:
    root = ROOT
    for kernel in (county_zip_join, point_in_counties, county_soil_overlay, central_ray_triangle_stats):
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
    triangles = make_random_triangles(8, seed=17)
    rays = make_center_rays(6, seed=19)
    hit_counts = rt.ray_triangle_hit_count_cpu(rays, triangles)
    print()
    print("Ray Query Sample")
    print("----------------")
    print(f"triangles      : {len(triangles)}")
    print(f"rays           : {len(rays)}")
    print(f"ray hit counts : {[record['hit_count'] for record in hit_counts]}")

    print()
    print("CPU Simulator Sample")
    print("--------------------")
    lsi_results = rt.run_cpu(
        county_zip_join,
        left=({"id": 1, "x0": 0.0, "y0": 0.0, "x1": 2.0, "y1": 2.0},),
        right=({"id": 2, "x0": 0.0, "y0": 2.0, "x1": 2.0, "y1": 0.0},),
    )
    pip_results = rt.run_cpu(
        point_in_counties,
        points=(
            {"id": 10, "x": 0.5, "y": 0.5},
            {"id": 11, "x": 3.0, "y": 3.0},
        ),
        polygons=(
            {"id": 20, "vertices": ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))},
        ),
    )
    overlay_results = rt.run_cpu(
        county_soil_overlay,
        left=(
            {"id": 30, "vertices": ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))},
        ),
        right=(
            {"id": 31, "vertices": ((1.0, -1.0), (3.0, -1.0), (3.0, 1.0), (1.0, 1.0))},
        ),
    )
    ray_results = rt.run_cpu(central_ray_triangle_stats, rays=rays, triangles=triangles)
    print(f"lsi rows       : {lsi_results}")
    print(f"pip rows       : {pip_results}")
    print(f"overlay rows   : {overlay_results}")
    print(f"ray rows       : {ray_results}")


if __name__ == "__main__":
    main()
