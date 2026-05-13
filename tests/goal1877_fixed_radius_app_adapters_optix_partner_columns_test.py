import unittest
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
REPORT = ROOT / "docs" / "reports" / "goal1877_fixed_radius_app_adapters_optix_partner_columns_2026-05-13.md"
SMOKE = ROOT / "docs" / "reports" / "goal1877_fixed_radius_app_adapters_optix_partner_columns_pod_smoke.json"


class Goal1877FixedRadiusAppAdaptersOptixPartnerColumnsTest(unittest.TestCase):
    def test_app_adapters_are_exported(self) -> None:
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("service_coverage_gap_flags_optix_partner_device_columns", init_text)
        self.assertIn("event_hotspot_flags_optix_partner_device_columns", init_text)

    def test_app_adapters_reuse_generic_fixed_radius_native_contract(self) -> None:
        adapter = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("def service_coverage_gap_flags_optix_partner_device_columns", adapter)
        self.assertIn("def event_hotspot_flags_optix_partner_device_columns", adapter)
        self.assertIn("fixed_radius_count_threshold_2d_optix_partner_device_columns", adapter)
        self.assertIn('"generic_fixed_radius_count_threshold_2d_device_columns"', adapter)
        self.assertIn("threshold=hotspot_threshold + 1", adapter)
        self.assertIn('"whole_app_speedup_claim_authorized": False', adapter)

    def test_report_keeps_release_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: pass-with-boundary", report)
        self.assertIn("generic_fixed_radius_count_threshold_2d_device_columns", report)
        self.assertIn("App semantics stay in Python", report)
        self.assertIn("does not create accepted v2.0 performance rows", report)
        self.assertIn("No v2.0 release claim", report)
        self.assertIn("Both Torch and CuPy matched those expected outputs", report)

    def test_pod_smoke_artifact_records_app_outputs(self) -> None:
        smoke = json.loads(SMOKE.read_text(encoding="utf-8"))

        self.assertEqual(smoke["observed"]["torch"]["service_coverage_gaps"]["uncovered_flags"], [0, 1, 0])
        self.assertEqual(smoke["observed"]["cupy"]["event_hotspot_screening"]["hotspot_flags"], [1, 1, 0])
        self.assertFalse(smoke["claim_boundaries"]["v2_0_release_authorized"])


if __name__ == "__main__":
    unittest.main()
