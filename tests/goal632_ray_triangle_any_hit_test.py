import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_any_hit_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "any_hit"])


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_any_hit_3d_kernel():
    rays = rt.input("rays", rt.Rays3D, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles3D, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "any_hit"])


class Goal632RayTriangleAnyHitTest(unittest.TestCase):
    def test_any_hit_predicate_is_public_and_lowers(self) -> None:
        compiled = rt.compile_kernel(ray_triangle_any_hit_kernel)
        plan = rt.lower_to_execution_plan(compiled)

        self.assertEqual(compiled.refine_op.predicate.name, "ray_triangle_any_hit")
        self.assertEqual(compiled.emit_op.fields, ("ray_id", "any_hit"))
        self.assertEqual(plan.workload_kind, "ray_tri_anyhit")
        self.assertIn("terminate traversal after the first accepted triangle hit", " ".join(plan.host_steps))

    def test_any_hit_cpu_collapses_hit_count_to_boolean(self) -> None:
        rays = (
            rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=10.0),
            rt.Ray2D(id=2, ox=0.0, oy=0.0, dx=0.0, dy=1.0, tmax=2.0),
        )
        triangles = (
            rt.Triangle(id=10, x0=2.0, y0=-1.0, x1=3.0, y1=1.0, x2=4.0, y2=-1.0),
            rt.Triangle(id=11, x0=6.0, y0=-1.0, x1=7.0, y1=1.0, x2=8.0, y2=-1.0),
            rt.Triangle(id=12, x0=-1.0, y0=3.0, x1=1.0, y1=3.0, x2=0.0, y2=4.0),
        )

        any_hit_rows = rt.ray_triangle_any_hit_cpu(rays, triangles)
        count_rows = rt.ray_triangle_hit_count_cpu(rays, triangles)

        self.assertEqual(any_hit_rows, ({"ray_id": 1, "any_hit": 1}, {"ray_id": 2, "any_hit": 0}))
        self.assertEqual(
            tuple({"ray_id": row["ray_id"], "any_hit": 1 if row["hit_count"] else 0} for row in count_rows),
            any_hit_rows,
        )

    def test_run_cpu_python_reference_and_run_cpu_match(self) -> None:
        inputs = {
            "rays": (
                rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=10.0),
                rt.Ray2D(id=2, ox=0.0, oy=0.0, dx=0.0, dy=1.0, tmax=2.0),
            ),
            "triangles": (
                rt.Triangle(id=10, x0=2.0, y0=-1.0, x1=3.0, y1=1.0, x2=4.0, y2=-1.0),
            ),
        }

        expected = ({"ray_id": 1, "any_hit": 1}, {"ray_id": 2, "any_hit": 0})
        self.assertEqual(rt.run_cpu_python_reference(ray_triangle_any_hit_kernel, **inputs), expected)
        self.assertEqual(rt.run_cpu(ray_triangle_any_hit_kernel, **inputs), expected)

    def test_run_cpu_supports_3d_any_hit_reference_fallback(self) -> None:
        inputs = {
            "rays": (
                rt.Ray3D(id=1, ox=0.0, oy=0.0, oz=0.0, dx=10.0, dy=0.0, dz=0.0, tmax=1.0),
                rt.Ray3D(id=2, ox=0.0, oy=2.0, oz=0.0, dx=10.0, dy=0.0, dz=0.0, tmax=1.0),
            ),
            "triangles": (
                rt.Triangle3D(id=20, x0=5.0, y0=-1.0, z0=-1.0, x1=5.0, y1=1.0, z1=-1.0, x2=5.0, y2=0.0, z2=1.0),
            ),
        }

        expected = ({"ray_id": 1, "any_hit": 1}, {"ray_id": 2, "any_hit": 0})
        self.assertEqual(rt.run_cpu_python_reference(ray_triangle_any_hit_3d_kernel, **inputs), expected)
        self.assertEqual(rt.run_cpu(ray_triangle_any_hit_3d_kernel, **inputs), expected)


if __name__ == "__main__":
    unittest.main()
