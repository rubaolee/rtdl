from pathlib import Path
import inspect
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3414_native_exact_page_producer_probe_2026-06-04.json"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
SCRIPT = ROOT / "scripts" / "goal3414_native_exact_page_producer_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3414_native_exact_page_producer_surface_2026-06-04.md"


class Goal3414NativeExactPageProducerSurfaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prelude = PRELUDE.read_text(encoding="utf-8")
        cls.api = API.read_text(encoding="utf-8")
        cls.workloads = WORKLOADS.read_text(encoding="utf-8")
        cls.runtime = RUNTIME.read_text(encoding="utf-8")
        cls.script = SCRIPT.read_text(encoding="utf-8")
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_native_page_symbol_is_declared_and_implemented(self):
        symbol = "rtdl_optix_prepared_point_closed_shape_membership_exact_device_columns_page_2d"
        self.assertIn(symbol, self.prelude)
        self.assertIn(f'extern "C" int {symbol}', self.api)
        self.assertIn("run_prepared_point_closed_shape_membership_exact_device_columns_page_2d_optix", self.api)
        self.assertIn("static void run_prepared_point_closed_shape_membership_exact_device_columns_page_2d_optix", self.workloads)
        self.assertIn("page_start > point_count", self.workloads)
        self.assertIn("page_count > point_count - page_start", self.workloads)
        self.assertIn("points + page_start", self.workloads)

    def test_python_runtime_exposes_explicit_page_method(self):
        import rtdsl.optix_runtime as optix_runtime

        symbol = "rtdl_optix_prepared_point_closed_shape_membership_exact_device_columns_page_2d"
        self.assertEqual(
            optix_runtime.OPTIX_CLOSED_SHAPE_MEMBERSHIP_EXACT_DEVICE_COLUMNS_PAGE_SYMBOL,
            symbol,
        )
        self.assertIn("OPTIX_CLOSED_SHAPE_MEMBERSHIP_EXACT_DEVICE_COLUMNS_PAGE_SYMBOL", self.runtime)
        self.assertIn("optional_closed_shape_exact_device_columns_page.argtypes", self.runtime)

        source = inspect.getsource(optix_runtime.PreparedOptixPointClosedShapeMembership2D.exact_device_columns_page)
        self.assertIn("page_start", source)
        self.assertIn("page_count", source)
        self.assertIn("packed_points.records", source)
        self.assertIn("ctypes.c_size_t(start)", source)
        self.assertIn("ctypes.c_size_t(count)", source)
        self.assertIn("OPTIX_CLOSED_SHAPE_MEMBERSHIP_EXACT_DEVICE_COLUMNS_PAGE_SYMBOL", source)

    def test_page_symbol_is_classified_as_exact_bridge_metadata(self):
        start = self.runtime.index("is_exact_closed_shape_bridge =")
        end = self.runtime.index('metadata["runtime"] =', start)
        block = self.runtime[start:end]
        self.assertIn("OPTIX_CLOSED_SHAPE_MEMBERSHIP_EXACT_DEVICE_COLUMNS_SYMBOL", block)
        self.assertIn("OPTIX_CLOSED_SHAPE_MEMBERSHIP_EXACT_DEVICE_COLUMNS_PAGE_SYMBOL", block)

    def test_probe_uses_native_page_range_not_python_slice_for_native_producer(self):
        self.assertIn("exact_device_columns_page(", self.script)
        self.assertIn("packed_points = rt.pack_points(records=points, dimension=2)", self.script)
        self.assertIn("exact_device_columns_page(\n                packed_points,", self.script)
        self.assertIn("page_start=request.start", self.script)
        self.assertIn("page_count=request.item_count", self.script)
        self.assertIn('"python_point_slicing_for_native_producer": False', self.script)
        self.assertIn('"single_packed_point_buffer_reused": True', self.script)
        self.assertIn('"native_page_plan_handle_implemented": False', self.script)
        self.assertIn('"device_only_exact_predicate_produced": False', self.script)

    def test_report_keeps_boundaries_clear(self):
        self.assertIn("not yet the full native paged stream ABI", self.report)
        self.assertIn("does not implement a page", self.report)
        self.assertIn("device-only exact predicates", self.report)
        self.assertIn("true zero-copy", self.report)
        self.assertIn("release", self.report)
        self.assertIn("authorization", self.report)
        self.assertIn("host-refined bridge", self.report)

    def test_pod_artifact_records_native_page_producer_evidence(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3414.native_exact_page_producer_probe.v1")
        self.assertEqual(payload["goal"], 3414)
        self.assertEqual(payload["rtdl_commit"][:8], "a50494bc")
        self.assertIn("NVIDIA RTX A5000", payload["gpu"])
        self.assertEqual(
            payload["native_page_symbol"],
            "rtdl_optix_prepared_point_closed_shape_membership_exact_device_columns_page_2d",
        )
        self.assertEqual(payload["point_count"], 16545)
        self.assertEqual(payload["shape_count"], 15700)

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

        native_page = payload["native_page_boundary"]
        self.assertTrue(native_page["native_page_producer_used"])
        self.assertTrue(native_page["native_call_uses_page_start_and_page_count"])
        self.assertFalse(native_page["python_point_slicing_for_native_producer"])
        self.assertTrue(native_page.get("single_packed_point_buffer_reused", True))
        self.assertFalse(native_page["native_page_plan_handle_implemented"])
        self.assertFalse(native_page["native_page_release_function_implemented"])
        self.assertFalse(native_page["device_only_exact_predicate_produced"])

        first_page = recovery["page_records"][0]
        last_page = recovery["page_records"][-1]
        self.assertEqual(first_page["first_capacity_status"]["required_capacity"], 5666)
        self.assertEqual(last_page["first_capacity_status"]["required_capacity"], 352)

        for key, value in payload["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
