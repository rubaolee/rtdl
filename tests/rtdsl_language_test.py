import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")

import rtdsl as rt
from examples.internal.rtdl_codex_authored import CODEX_AUTHORED_KERNELS
from examples.internal.rtdl_gemini_authored import GEMINI_AUTHORED_KERNELS
from examples.reference.rtdl_workload_reference import WORKLOAD_REFERENCE_KERNELS
from examples.reference.rtdl_language_reference import LANGUAGE_REFERENCE_KERNELS
from examples.reference.rtdl_ray_tri_hitcount import ray_triangle_hitcount_reference


class RtDslLanguageTest(unittest.TestCase):
    docs_dir = Path("docs/rtdl")

    def setUp(self) -> None:
        self.output_dir = Path(tempfile.mkdtemp(prefix="rtdsl_language_examples_", dir="build"))
        self.addCleanup(shutil.rmtree, self.output_dir, ignore_errors=True)

    def _generate(self, kernel_fn):
        compiled = rt.compile_kernel(kernel_fn)
        plan = rt.lower_to_execution_plan(compiled)
        target_dir = self.output_dir / compiled.name

        generated = rt.generate_optix_project(plan, target_dir)
        return compiled, plan, generated

    def test_language_docs_exist(self) -> None:
        for path in (
            self.docs_dir / "README.md",
            self.docs_dir / "dsl_reference.md",
            self.docs_dir / "programming_guide.md",
            self.docs_dir / "workload_cookbook.md",
            self.docs_dir / "llm_authoring_guide.md",
        ):
            self.assertTrue(path.exists(), msg=f"missing docs file: {path}")

    def test_reference_examples_compile_and_lower(self) -> None:
        expected = {
            "county_zip_join_reference": "lsi",
            "point_in_counties_reference": "pip",
            "county_soil_overlay_reference": "overlay",
            "ray_triangle_hitcount_reference": "ray_tri_hitcount",
            "segment_polygon_hitcount_reference": "segment_polygon_hitcount",
            "segment_polygon_anyhit_rows_reference": "segment_polygon_anyhit_rows",
            "point_nearest_segment_reference": "point_nearest_segment",
        }

        for kernel_fn in LANGUAGE_REFERENCE_KERNELS + (ray_triangle_hitcount_reference,) + WORKLOAD_REFERENCE_KERNELS:
            compiled, plan, generated = self._generate(kernel_fn)
            self.assertEqual(plan.workload_kind, expected[compiled.name])
            payload = json.loads(generated["metadata"].read_text(encoding="utf-8"))
            rt.validate_plan_dict(payload)

    def test_codex_authored_examples_compile_and_lower(self) -> None:
        expected = {
            "road_boundary_crossings": "lsi",
            "station_in_districts": "pip",
            "parcel_flood_overlay": "overlay",
        }

        for kernel_fn in CODEX_AUTHORED_KERNELS:
            compiled, plan, generated = self._generate(kernel_fn)
            self.assertEqual(plan.workload_kind, expected[compiled.name])
            payload = json.loads(generated["metadata"].read_text(encoding="utf-8"))
            rt.validate_plan_dict(payload)

    def test_gemini_authored_examples_compile_and_lower(self) -> None:
        expected = {
            "lsi_kernel": "lsi",
            "pip_kernel": "pip",
            "overlay_kernel": "overlay",
        }

        for kernel_fn in GEMINI_AUTHORED_KERNELS:
            compiled, plan, generated = self._generate(kernel_fn)
            self.assertEqual(plan.workload_kind, expected[compiled.name])
            payload = json.loads(generated["metadata"].read_text(encoding="utf-8"))
            rt.validate_plan_dict(payload)

    def test_llm_guide_states_current_surface(self) -> None:
        guide = (self.docs_dir / "llm_authoring_guide.md").read_text(encoding="utf-8")
        self.assertIn("precision=\"float_approx\"", guide)
        self.assertIn("segment_intersection(exact=False)", guide)
        self.assertIn("point_in_polygon(exact=False, boundary_mode=\"inclusive\")", guide)
        self.assertIn("overlay_compose()", guide)
        self.assertIn("ray_triangle_hit_count(exact=False)", guide)
        self.assertIn("segment_polygon_hitcount(exact=False)", guide)
        self.assertIn("point_nearest_segment(exact=False)", guide)


if __name__ == "__main__":
    unittest.main()
