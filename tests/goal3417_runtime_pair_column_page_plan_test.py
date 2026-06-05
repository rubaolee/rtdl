from pathlib import Path
import inspect
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3417_runtime_page_plan_probe_2026-06-04.json"
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

    def test_pod_artifact_records_runtime_page_plan_evidence(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3417.runtime_page_plan_probe.v1")
        self.assertEqual(payload["goal"], 3417)
        self.assertEqual(payload["rtdl_commit"][:8], "15970d94")
        self.assertIn("NVIDIA RTX A5000", payload["gpu"])
        self.assertEqual(payload["point_count"], 16545)
        self.assertEqual(payload["shape_count"], 15700)

        page_plan = payload["page_plan"]
        self.assertEqual(page_plan["schema"], "rtdl.optix.exact_device_pair_column_page_plan.v1")
        self.assertTrue(page_plan["runtime_page_plan_object"])
        self.assertTrue(page_plan["single_packed_point_buffer_reused"])
        self.assertTrue(page_plan["native_page_producer_used_by_plan"])
        self.assertFalse(page_plan["native_page_plan_handle_implemented"])
        self.assertFalse(page_plan["native_page_release_function_implemented"])
        self.assertFalse(page_plan["automatic_retry_authorized"])
        self.assertFalse(page_plan["hidden_dispatch_authorized"])
        self.assertEqual(page_plan["page_count"], 9)
        self.assertEqual(page_plan["page_requests"][0]["start"], 0)
        self.assertEqual(page_plan["page_requests"][-1]["item_count"], 161)

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

        boundary = payload["runtime_page_plan_boundary"]
        self.assertTrue(boundary["runtime_page_plan_object_used"])
        self.assertTrue(boundary["single_packed_point_buffer_reused"])
        self.assertTrue(boundary["produce_page_api_used"])
        self.assertFalse(boundary["native_page_plan_handle_implemented"])
        self.assertFalse(boundary["native_page_release_function_implemented"])

        for key, value in payload["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
