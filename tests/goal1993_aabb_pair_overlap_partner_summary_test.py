from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
EXAMPLE = ROOT / "examples" / "rtdl_control_apps_cupy_rawkernel.py"
REPORT = ROOT / "docs" / "reports" / "goal1993_aabb_pair_overlap_partner_summary_2026-05-14.md"


class Goal1993AabbPairOverlapPartnerSummaryTest(unittest.TestCase):
    def test_generic_aabb_partner_summary_is_public(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("def aabb_pair_overlap_summary_2d_partner_columns", adapters)
        self.assertIn("generic_aabb_pair_overlap_summary_2d", adapters)
        self.assertIn("_cupy_aabb_pair_overlap_summary_2d", adapters)
        self.assertIn("not_called_partner_reference_only", adapters)
        self.assertIn("from .partner_adapters import aabb_pair_overlap_summary_2d_partner_columns", init_text)
        self.assertIn('"aabb_pair_overlap_summary_2d_partner_columns"', init_text)

    def test_polygon_control_path_uses_generic_aabb_summary_not_app_extent_kernel(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")

        self.assertIn("aabb_pair_overlap_summary_2d_partner_columns", text)
        self.assertIn("_pair_extent_partner_columns", text)
        self.assertIn('"aabb_pair_overlap_summary_2d_partner_columns"', text)
        self.assertNotIn("POLYGON_EXTENT_RAWKERNEL_SOURCE", text)
        self.assertNotIn("rtdl_user_pair_extent_summary", text)

    def test_cpu_fallback_polygon_controls_still_match_oracles(self) -> None:
        for app in ("polygon_pair_overlap_area_rows", "polygon_set_jaccard"):
            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXAMPLE),
                    "--app",
                    app,
                    "--copies",
                    "2",
                    "--partner",
                    "cpu_fallback",
                    "--candidate-backend",
                    "cpu_all_pairs",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["matches_v1_8_python_rtdl_oracle"], app)

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("generic 2D AABB", report)
        self.assertIn("pair-overlap summary", report)
        self.assertIn("not arbitrary polygon", report)
        self.assertIn("overlay", report)
        self.assertIn("does not customize the RTDL native engine", report)


if __name__ == "__main__":
    unittest.main()
