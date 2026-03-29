import rtdsl as rt

from examples.rtdl_language_reference import county_soil_overlay_reference
from examples.rtdl_language_reference import county_zip_join_reference
from examples.rtdl_language_reference import point_in_counties_reference
from examples.rtdl_ray_tri_hitcount import make_center_rays
from examples.rtdl_ray_tri_hitcount import make_random_triangles
from examples.rtdl_ray_tri_hitcount import ray_triangle_hitcount_reference


def main() -> None:
    left_segments = (
        {"id": 1, "x0": 0.0, "y0": 0.0, "x1": 2.0, "y1": 2.0},
        {"id": 2, "x0": 2.0, "y0": 0.0, "x1": 2.0, "y1": 2.0},
    )
    right_segments = (
        {"id": 10, "x0": 0.0, "y0": 2.0, "x1": 2.0, "y1": 0.0},
    )
    print("LSI:", rt.run_cpu(county_zip_join_reference, left=left_segments, right=right_segments))

    points = (
        {"id": 100, "x": 0.5, "y": 0.5},
        {"id": 101, "x": 3.0, "y": 3.0},
    )
    polygons = (
        {"id": 200, "vertices": ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))},
    )
    print("PIP:", rt.run_cpu(point_in_counties_reference, points=points, polygons=polygons))

    left_polygons = (
        {"id": 300, "vertices": ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))},
    )
    right_polygons = (
        {"id": 301, "vertices": ((1.0, -1.0), (3.0, -1.0), (3.0, 1.0), (1.0, 1.0))},
    )
    print("OVERLAY:", rt.run_cpu(county_soil_overlay_reference, left=left_polygons, right=right_polygons))

    triangles = make_random_triangles(5, seed=7)
    rays = make_center_rays(4, seed=11)
    print("RAY HITCOUNT:", rt.run_cpu(ray_triangle_hitcount_reference, rays=rays, triangles=triangles))


if __name__ == "__main__":
    main()
