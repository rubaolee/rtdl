import rtdsl as rt
from pathlib import Path


@rt.kernel(backend="rayjoin", precision="float_approx")
def county_zip_join():
    segment_layout = rt.layout(
        "Segment2D",
        rt.field("x0", rt.f32),
        rt.field("y0", rt.f32),
        rt.field("x1", rt.f32),
        rt.field("y1", rt.f32),
        rt.field("id", rt.u32),
    )
    left = rt.input("left", rt.Segments, layout=segment_layout, role="probe")
    right = rt.input("right", rt.Segments, layout=segment_layout, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(
        hits,
        fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
    )


def main() -> None:
    compiled = rt.compile_kernel(county_zip_join)
    plan = rt.lower_to_rayjoin(compiled)
    generated = rt.generate_optix_project(
        plan,
        Path(__file__).resolve().parents[1] / "generated" / compiled.name,
    )

    print(compiled.format())
    print()
    print(plan.format())
    print()
    print("Generated Files")
    print("---------------")
    for label, path in generated.items():
        print(f"{label:8}: {path}")


if __name__ == "__main__":
    main()
