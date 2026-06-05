from pathlib import Path
import inspect
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
SCRIPT = ROOT / "scripts" / "goal3417_runtime_page_plan_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3417_runtime_pair_column_page_plan_2026-06-04.md"


class Goal3417RuntimePairColumnPagePlanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = RUNTIME.read_text(encoding="utf-8")
        cls.script = SCRIPT.read_text(encoding="utf-8")
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_runtime_page_plan_surface_exists(self):
        import rtdsl.optix_runtime as optix_runtime

        self.assertTrue(hasattr(optix_runtime, "OptixExactDevicePairColumnPagePlan"))
        source = inspect.getsource(optix_runtime.OptixExactDevicePairColumnPagePlan)
        self.assertIn("def produce_page", source)
        self.assertIn("exact_device_columns_page", source)
        self.assertIn("single_packed_point_buffer_reused", source)
        self.assertIn("native_page_plan_handle_implemented", source)
        self.assertIn("automatic_retry_authorized", source)

        method = inspect.getsource(
            optix_runtime.PreparedOptixPointClosedShapeMembership2D.exact_device_columns_page_plan
        )
        self.assertIn("pack_points(records=points, dimension=2)", method)
        self.assertIn("iter_pair_column_page_requests", method)
        self.assertIn("OptixExactDevicePairColumnPagePlan", method)

    def test_probe_uses_page_plan_and_produce_page(self):
        self.assertIn("exact_device_columns_page_plan", self.script)
        self.assertIn("page_plan.produce_page(request.page_index)", self.script)
        self.assertIn("page_plan.produce_page(request.page_index, max_rows=retry_hint)", self.script)
        self.assertIn('"runtime_page_plan_object_used": True', self.script)
        self.assertIn('"single_packed_point_buffer_reused": True', self.script)
        self.assertIn('"native_page_plan_handle_implemented": False', self.script)

    def test_report_keeps_native_handle_boundary(self):
        self.assertIn("runtime page plan", self.report)
        self.assertIn("not a native page-plan handle", self.report)
        self.assertIn("single_packed_point_buffer_reused", self.report)
        self.assertIn("native_page_plan_handle_implemented = False", self.report)
        self.assertIn("host-refined exact bridge", self.report)
        self.assertIn("release_page", self.report)


if __name__ == "__main__":
    unittest.main()
