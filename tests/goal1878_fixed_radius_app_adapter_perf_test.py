import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1878_fixed_radius_app_adapter_perf.py"
REPORT = ROOT / "docs" / "reports" / "goal1878_fixed_radius_app_adapter_perf_2026-05-13.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal1878_fixed_radius_app_adapter_perf_pod.json"


class Goal1878FixedRadiusAppAdapterPerfTest(unittest.TestCase):
    def test_script_exists_and_uses_three_way_comparison(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("v1_8_prepared_optix", script)
        self.assertIn("goal1873_partner_reference", script)
        self.assertIn("goal1877_v2_native_optix_partner", script)
        self.assertIn("service_coverage_gap_flags_optix_partner_device_columns", script)
        self.assertIn("event_hotspot_flags_optix_partner_device_columns", script)
        self.assertIn("RTDL_SOURCE_COMMIT_LABEL", script)
        self.assertIn("nvidia-smi", script)

    def test_artifact_records_all_apps_partners_and_boundaries(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["goal"], 1878)
        self.assertEqual(len(payload["results"]), 4)
        partners = {row["partner"] for row in payload["results"]}
        self.assertEqual(partners, {"torch", "cupy"})
        for row in payload["results"]:
            self.assertIn("service_coverage_gaps", row)
            self.assertIn("event_hotspot_screening", row)
            self.assertFalse(row["claim_boundaries"]["v2_0_release_authorized"])

    def test_report_does_not_overclaim_rt_speedup(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: measured-with-boundary", report)
        self.assertIn("partner-reference tensor path is still faster", report)
        self.assertIn("not authorize broad RT-core speedup wording", report)
        self.assertIn("does not authorize", report)


if __name__ == "__main__":
    unittest.main()
