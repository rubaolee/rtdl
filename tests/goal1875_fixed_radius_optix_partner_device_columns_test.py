import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPTIX_API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
OPTIX_CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
OPTIX_WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
REPORT = ROOT / "docs" / "reports" / "goal1875_fixed_radius_optix_partner_device_columns_2026-05-13.md"
SMOKE = ROOT / "docs" / "reports" / "goal1875_fixed_radius_optix_partner_device_columns_pod_smoke.json"


class Goal1875FixedRadiusOptixPartnerDeviceColumnsTest(unittest.TestCase):
    def test_native_symbols_and_device_column_kernel_exist(self) -> None:
        api = OPTIX_API.read_text(encoding="utf-8")
        core = OPTIX_CORE.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_prepare_fixed_radius_count_threshold_2d_device_search_columns", api)
        self.assertIn("rtdl_optix_write_prepared_fixed_radius_count_threshold_2d_device_query_columns", api)
        self.assertIn("pack_point2d_fixed_radius_aabbs", core)
        self.assertIn("use_device_columns", core)
        self.assertIn("search_columns_zero_copy", workloads)
        self.assertIn("write_prepared_fixed_radius_count_threshold_2d_device_query_columns_optix", workloads)

    def test_python_runtime_exports_device_search_and_output_path(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("prepare_optix_fixed_radius_count_threshold_2d_device_search_columns", runtime)
        self.assertIn("write_device_count_threshold_columns", runtime)
        self.assertIn("device_fixed_radius_point_columns_output_columns_zero_copy", runtime)
        self.assertIn("prepare_optix_fixed_radius_count_threshold_2d_device_search_columns", init_text)

    def test_partner_adapter_marks_exact_claim_boundary(self) -> None:
        adapter = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("fixed_radius_count_threshold_2d_optix_partner_device_columns", adapter)
        self.assertIn("generic_fixed_radius_count_threshold_2d_device_columns", adapter)
        self.assertIn('"native_symbol": "not_called_empty_input"', adapter)
        self.assertIn('"v2_0_release_authorized": False', adapter)
        self.assertIn('"whole_app_speedup_claim_authorized": False', adapter)

    def test_report_and_pod_smoke_preserve_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        smoke = json.loads(SMOKE.read_text(encoding="utf-8"))

        self.assertIn("Status: pass-with-boundary", report)
        self.assertIn("generic_fixed_radius_count_threshold_2d_device_columns", report)
        self.assertIn("does not authorize", report)
        self.assertEqual(smoke["observed"]["torch"]["neighbor_counts"], [2, 1, 1])
        self.assertEqual(smoke["observed"]["cupy"]["threshold_flags"], [1, 0, 0])
        self.assertTrue(smoke["observed"]["torch"]["true_zero_copy_authorized"])
        self.assertFalse(smoke["claim_boundaries"]["v2_0_release_authorized"])


if __name__ == "__main__":
    unittest.main()
