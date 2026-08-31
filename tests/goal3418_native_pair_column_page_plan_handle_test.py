from pathlib import Path
import inspect
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3418_native_page_plan_handle_probe_2026-06-04.json"
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

    def test_pod_artifact_records_native_page_plan_handle_evidence(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3418.native_page_plan_handle_probe.v1")
        self.assertEqual(payload["goal"], 3418)
        self.assertEqual(payload["rtdl_commit"][:8], "c0bedc29")
        self.assertIn("NVIDIA RTX A5000", payload["gpu"])
        self.assertEqual(payload["point_count"], 16545)
        self.assertEqual(payload["shape_count"], 15700)

        native_plan = payload["native_page_plan"]
        self.assertEqual(native_plan["schema"], "rtdl.optix.native_exact_device_pair_column_page_plan.v1")
        self.assertTrue(native_plan["native_page_plan_handle_implemented"])
        self.assertTrue(native_plan["native_page_release_function_implemented"])
        self.assertTrue(native_plan["native_page_producer_used_by_plan"])
        self.assertFalse(native_plan["automatic_retry_authorized"])
        self.assertFalse(native_plan["hidden_dispatch_authorized"])
        self.assertFalse(native_plan["device_only_exact_predicate_produced"])
        self.assertEqual(native_plan["item_count"], 16545)
        self.assertEqual(native_plan["page_size"], 2048)
        self.assertEqual(native_plan["page_count"], 9)
        self.assertEqual(native_plan["initial_capacity"], 100)

        recovery = payload["recovery_summary"]
        self.assertEqual(recovery["page_count"], 9)
        self.assertEqual(recovery["overflow_page_count"], 9)
        self.assertEqual(recovery["retry_page_count"], 9)
        self.assertEqual(recovery["grouped_source_row_count"], 47262)
        self.assertEqual(recovery["grouped_row_count"], 16541)
        self.assertEqual(recovery["merge_rule"], "key_addition")
        self.assertFalse(recovery["merge_requires_disjoint_keys"])

        self.assertEqual(payload["host_exact_row_count"], 47262)
        self.assertEqual(payload["device_grouped_source_row_count"], 47262)
        self.assertEqual(payload["host_group_count"], 16476)
        self.assertEqual(payload["device_group_count"], 16476)
        self.assertTrue(payload["group_counts_match_host"])
        self.assertEqual(payload["missing_group_key_count"], 0)
        self.assertEqual(payload["extra_group_key_count"], 0)
        self.assertEqual(payload["mismatched_group_value_count"], 0)

        boundary = payload["native_page_plan_boundary"]
        self.assertTrue(boundary["native_page_plan_handle_implemented"])
        self.assertTrue(boundary["native_page_release_function_implemented"])
        self.assertTrue(boundary["native_plan_owns_host_point_copy"])
        self.assertTrue(boundary["produce_page_api_used"])
        self.assertFalse(boundary["device_only_exact_predicate_produced"])
        self.assertFalse(boundary["automatic_retry_authorized"])
        self.assertFalse(boundary["hidden_dispatch_authorized"])

        for key, value in payload["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
