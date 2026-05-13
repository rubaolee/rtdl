from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1872_fixed_radius_partner_device_column_gap_2026-05-13.md"
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
GOAL1843 = ROOT / "docs" / "reports" / "goal1843_v2_0_vs_v1_8_total_perf_readiness_2026-05-13.md"


class Goal1872FixedRadiusPartnerDeviceColumnGapTest(unittest.TestCase):
    def test_report_identifies_fixed_radius_apps_as_blocked(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: needs-implementation", report)
        self.assertIn("service_coverage_gaps", report)
        self.assertIn("event_hotspot_screening", report)
        self.assertIn("fixed-radius count-threshold primitive", report)
        self.assertIn("caller-owned query point CUDA columns", report)
        self.assertIn("Torch reference behavior and CuPy conformance", report)
        self.assertIn("No v2.0 release wording", report)

    def test_current_partner_adapters_do_not_yet_expose_fixed_radius_device_columns(self) -> None:
        adapter_text = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        self.assertNotIn("fixed_radius", adapter_text)
        self.assertNotIn("service_coverage_gaps_optix_partner", adapter_text)
        self.assertNotIn("event_hotspot_screening_optix_partner", adapter_text)

    def test_current_optix_fixed_radius_path_is_host_packed(self) -> None:
        runtime_text = OPTIX_RUNTIME.read_text(encoding="utf-8")

        self.assertIn("PreparedOptixFixedRadiusCountThreshold2D", runtime_text)
        self.assertIn("PackedPoints", runtime_text)
        self.assertIn("pack_points(records=query_points, dimension=2)", runtime_text)
        self.assertNotIn("prepare_optix_fixed_radius_count_threshold_2d_device", runtime_text)

    def test_goal1843_keeps_fixed_radius_apps_not_rewritten_for_partner(self) -> None:
        text = GOAL1843.read_text(encoding="utf-8")

        self.assertIn("`service_coverage_gaps`", text)
        self.assertIn("`event_hotspot_screening`", text)
        self.assertIn("candidate after any-hit/count partner app adapter", text)


if __name__ == "__main__":
    unittest.main()
