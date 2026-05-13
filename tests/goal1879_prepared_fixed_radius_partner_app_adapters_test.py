import unittest
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
SCRIPT = ROOT / "scripts" / "goal1878_fixed_radius_app_adapter_perf.py"
REPORT = ROOT / "docs" / "reports" / "goal1879_prepared_fixed_radius_partner_app_adapters_2026-05-13.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal1879_fixed_radius_app_adapter_perf_prepared_pod.json"


class Goal1879PreparedFixedRadiusPartnerAppAdaptersTest(unittest.TestCase):
    def test_prepared_helpers_are_exported(self) -> None:
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene", init_text)
        self.assertIn("fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns", init_text)
        self.assertIn("service_coverage_gap_flags_optix_prepared_partner_device_columns", init_text)
        self.assertIn("event_hotspot_flags_optix_prepared_partner_device_columns", init_text)

    def test_prepared_adapters_reuse_same_generic_contract(self) -> None:
        adapter = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("def fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns", adapter)
        self.assertIn("def service_coverage_gap_flags_optix_prepared_partner_device_columns", adapter)
        self.assertIn("def event_hotspot_flags_optix_prepared_partner_device_columns", adapter)
        self.assertIn("generic_fixed_radius_count_threshold_2d_device_columns", adapter)
        self.assertIn('"native_optix_prepared_device_columns"', adapter)
        self.assertIn('"v2_0_release_authorized": False', adapter)

    def test_timing_harness_includes_prepared_native_rows(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("goal1879_v2_prepared_native_optix_partner", script)
        self.assertIn("service_coverage_gap_flags_optix_prepared_partner_device_columns", script)
        self.assertIn("event_hotspot_flags_optix_prepared_partner_device_columns", script)

    def test_report_preserves_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: measured-with-boundary", report)
        self.assertIn("avoid rebuilding the OptiX fixed-radius search GAS", report)
        self.assertIn("does not authorize v2.0 release", report)
        self.assertIn("partner-reference tensor path remains faster", report)

    def test_prepared_timing_artifact_includes_goal1879_rows(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["goal"], 1878)
        for row in payload["results"]:
            self.assertIn("goal1879_v2_prepared_native_optix_partner", row["service_coverage_gaps"])
            self.assertIn("goal1879_v2_prepared_native_optix_partner", row["event_hotspot_screening"])
            self.assertFalse(row["claim_boundaries"]["broad_rt_core_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
