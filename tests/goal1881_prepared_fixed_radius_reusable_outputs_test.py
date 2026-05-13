import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
SCRIPT = ROOT / "scripts" / "goal1878_fixed_radius_app_adapter_perf.py"
REPORT = ROOT / "docs" / "reports" / "goal1881_prepared_fixed_radius_reusable_outputs_2026-05-13.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal1881_fixed_radius_reusable_outputs_pod.json"


class Goal1881PreparedFixedRadiusReusableOutputsTest(unittest.TestCase):
    def test_allocator_is_exported(self) -> None:
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn(
            "allocate_fixed_radius_count_threshold_2d_partner_device_output_columns",
            init_text,
        )

    def test_prepared_adapter_accepts_reusable_output_columns(self) -> None:
        adapter = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        self.assertIn(
            "def allocate_fixed_radius_count_threshold_2d_partner_device_output_columns",
            adapter,
        )
        self.assertIn("output_columns: dict[str, object] | None = None", adapter)
        self.assertIn('"output_columns_reused": output_reuse_authorized', adapter)
        self.assertIn("fixed_radius_output_columns: dict[str, object] | None = None", adapter)
        self.assertIn("output_columns=fixed_radius_output_columns", adapter)
        self.assertIn("def _require_fixed_radius_output_column_lengths", adapter)
        self.assertIn("length must match query point count", adapter)

    def test_perf_harness_reuses_outputs_for_prepared_rows(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("allocate_fixed_radius_count_threshold_2d_partner_device_output_columns", script)
        self.assertIn("service_outputs =", script)
        self.assertIn("hotspot_outputs =", script)
        self.assertIn("fixed_radius_output_columns=service_outputs", script)
        self.assertIn("fixed_radius_output_columns=hotspot_outputs", script)
        self.assertIn("[goal1878] start case", script)
        self.assertIn("--max-reference-pairs", script)
        self.assertIn("v1_8_reused_prepared_optix", script)

    def test_report_keeps_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: measured-with-boundary", report)
        self.assertIn("reuses partner-owned output columns", report)
        self.assertIn("does not change the native ABI", report)
        self.assertIn("does not authorize broad RT-core speedup wording", report)
        self.assertIn("Speedup vs reused v1.8", report)
        self.assertIn("Dense partner-reference rows for size 16384 were intentionally skipped", report)

    def test_pod_artifact_records_fair_reused_v1_8_baseline(self) -> None:
        import json

        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "measurement")
        for row in payload["results"]:
            for app_name in ("service_coverage_gaps", "event_hotspot_screening"):
                app = row[app_name]
                self.assertIn("v1_8_reused_prepared_optix", app)
                self.assertIn("goal1879_v2_prepared_native_optix_partner", app)
                self.assertLess(
                    app["goal1879_v2_prepared_native_optix_partner"]["median_s"],
                    app["v1_8_reused_prepared_optix"]["median_s"],
                )
        large_rows = [row for row in payload["results"] if row["size"] == 16384]
        self.assertTrue(large_rows)
        for row in large_rows:
            self.assertEqual(row["service_coverage_gaps"]["goal1873_partner_reference"]["status"], "skipped")
            self.assertFalse(row["claim_boundaries"]["broad_rt_core_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
