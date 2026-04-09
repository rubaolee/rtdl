import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.internal.rtdl_codex_ray_query import CODEX_RAY_QUERY_KERNELS
from examples.internal.rtdl_gemini_ray_query import GEMINI_RAY_QUERY_KERNELS
from examples.reference.rtdl_ray_tri_hitcount import RAY_QUERY_REFERENCE_KERNELS


class RtDslRayQueryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.output_dir = Path(tempfile.mkdtemp(prefix="rtdsl_ray_query_examples_", dir="build"))
        self.addCleanup(shutil.rmtree, self.output_dir, ignore_errors=True)

    def _generate(self, kernel_fn):
        compiled = rt.compile_kernel(kernel_fn)
        plan = rt.lower_to_execution_plan(compiled)
        target_dir = self.output_dir / compiled.name

        generated = rt.generate_optix_project(plan, target_dir)
        return compiled, plan, generated

    def test_reference_ray_query_examples_compile_and_lower(self) -> None:
        for kernel_fn in RAY_QUERY_REFERENCE_KERNELS:
            compiled, plan, generated = self._generate(kernel_fn)
            self.assertEqual(plan.workload_kind, "ray_tri_hitcount")
            self.assertEqual(compiled.emit_op.fields, ("ray_id", "hit_count"))
            payload = json.loads(generated["metadata"].read_text(encoding="utf-8"))
            rt.validate_plan_dict(payload)

    def test_codex_ray_query_examples_compile_and_lower(self) -> None:
        for kernel_fn in CODEX_RAY_QUERY_KERNELS:
            compiled, plan, generated = self._generate(kernel_fn)
            self.assertEqual(plan.workload_kind, "ray_tri_hitcount")
            self.assertEqual(compiled.emit_op.fields, ("ray_id", "hit_count"))
            payload = json.loads(generated["metadata"].read_text(encoding="utf-8"))
            rt.validate_plan_dict(payload)

    def test_gemini_ray_query_examples_compile_and_lower(self) -> None:
        for kernel_fn in GEMINI_RAY_QUERY_KERNELS:
            compiled, plan, generated = self._generate(kernel_fn)
            self.assertEqual(plan.workload_kind, "ray_tri_hitcount")
            self.assertEqual(compiled.emit_op.fields, ("ray_id", "hit_count"))
            payload = json.loads(generated["metadata"].read_text(encoding="utf-8"))
            rt.validate_plan_dict(payload)

    def test_reference_hit_count_cpu(self) -> None:
        rays = (
            rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=10.0),
            rt.Ray2D(id=2, ox=0.0, oy=0.0, dx=0.0, dy=1.0, tmax=2.0),
        )
        triangles = (
            rt.Triangle(id=10, x0=2.0, y0=-1.0, x1=3.0, y1=1.0, x2=4.0, y2=-1.0),
            rt.Triangle(id=11, x0=6.0, y0=-1.0, x1=7.0, y1=1.0, x2=8.0, y2=-1.0),
            rt.Triangle(id=12, x0=-1.0, y0=3.0, x1=1.0, y1=3.0, x2=0.0, y2=4.0),
        )

        results = rt.ray_triangle_hit_count_cpu(rays, triangles)
        self.assertEqual(results[0]["ray_id"], 1)
        self.assertEqual(results[0]["hit_count"], 2)
        self.assertEqual(results[1]["ray_id"], 2)
        self.assertEqual(results[1]["hit_count"], 0)

    def test_lower_rejects_wrong_ray_query_geometry(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def bad_ray_query():
            rays = rt.input("rays", rt.Rays, role="build")
            triangles = rt.input("triangles", rt.Triangles, role="probe")
            candidates = rt.traverse(rays, triangles, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
            return rt.emit(hits, fields=["ray_id", "hit_count"])

        with self.assertRaisesRegex(ValueError, "triangle build input and ray probe input"):
            rt.lower_to_execution_plan(rt.compile_kernel(bad_ray_query))


if __name__ == "__main__":
    unittest.main()
