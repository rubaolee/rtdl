from pathlib import Path
import inspect
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
SCRIPT = ROOT / "scripts" / "goal3418_native_page_plan_handle_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3418_native_pair_column_page_plan_handle_2026-06-04.md"


class Goal3418NativePairColumnPagePlanHandleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prelude = PRELUDE.read_text(encoding="utf-8")
        cls.api = API.read_text(encoding="utf-8")
        cls.workloads = WORKLOADS.read_text(encoding="utf-8")
        cls.runtime = RUNTIME.read_text(encoding="utf-8")
        cls.script = SCRIPT.read_text(encoding="utf-8")
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_native_page_plan_abi_is_declared_and_wrapped(self):
        for symbol in (
            "rtdl_optix_prepare_point_closed_shape_membership_exact_device_columns_page_plan_2d",
            "rtdl_optix_produce_point_closed_shape_membership_exact_device_columns_page_2d",
            "rtdl_optix_destroy_point_closed_shape_membership_exact_device_columns_page_plan_2d",
        ):
            self.assertIn(symbol, self.prelude)
            self.assertIn(symbol, self.api)
            self.assertIn(symbol, self.runtime)
        self.assertIn("RtdlNativePairColumnPagePlanInfo", self.prelude)
        self.assertIn("NativeClosedShapeExactDeviceColumnPagePlan2D", self.workloads)
        self.assertIn("std::vector<RtdlPoint> points", self.workloads)
        self.assertIn("fill_native_pair_column_page_plan_info", self.workloads)

    def test_python_native_page_plan_surface_exists(self):
        import rtdsl.optix_runtime as optix_runtime

        self.assertTrue(hasattr(optix_runtime, "OptixExactDevicePairColumnNativePagePlan"))
        source = inspect.getsource(optix_runtime.OptixExactDevicePairColumnNativePagePlan)
        self.assertIn("def produce_page", source)
        self.assertIn("native_page_plan_handle_implemented", source)
        self.assertIn("native_page_release_function_implemented", source)
        self.assertIn("device_only_exact_predicate_produced", source)
        self.assertIn("def close", source)

        method = inspect.getsource(
            optix_runtime.PreparedOptixPointClosedShapeMembership2D.exact_device_columns_native_page_plan
        )
        self.assertIn("OPTIX_CLOSED_SHAPE_MEMBERSHIP_EXACT_DEVICE_COLUMNS_PAGE_PLAN_PREPARE_SYMBOL", method)
        self.assertIn("_RtdlNativePairColumnPagePlanInfo", method)
        self.assertIn("_OptixNativePairColumnPagePlanOwner", method)

    def test_probe_uses_native_plan_handle_and_preserves_boundaries(self):
        self.assertIn("exact_device_columns_native_page_plan", self.script)
        self.assertIn("native_plan.produce_page(page_index)", self.script)
        self.assertIn("native_plan.close()", self.script)
        self.assertIn('"native_page_plan_handle_implemented": True', self.script)
        self.assertIn('"native_plan_owns_host_point_copy": True', self.script)
        self.assertIn('"device_only_exact_predicate_produced": False', self.script)
        self.assertIn('"automatic_retry_authorized": False', self.script)

    def test_report_keeps_remaining_native_gap_clear(self):
        self.assertIn("first native", self.report)
        self.assertIn("owns a copied host point buffer", self.report)
        self.assertIn("not the final device-resident paged stream ABI", self.report)
        self.assertIn("device-only exact predicates", self.report)
        self.assertIn("true zero-copy", self.report)
        self.assertIn("release authorization", self.report)


if __name__ == "__main__":
    unittest.main()
