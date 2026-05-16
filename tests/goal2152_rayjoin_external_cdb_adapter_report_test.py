from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2152_rayjoin_external_cdb_adapter_2026-05-16.md"
APP = ROOT / "examples" / "rtdl_rayjoin_v2_spatial_join_app.py"


class Goal2152RayjoinExternalCdbAdapterReportTest(unittest.TestCase):
    def test_report_records_adapter_contract_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "external RayJoin CDB files",
            "points.cdb + polygons.cdb",
            "left.cdb + right.cdb",
            "This goal changes only the Python app-level adapter",
            "does not add C/C++ symbols",
            "new native app-specific engine functionality",
            "Goal2153 carries the first pod/public-data evidence",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_app_exposes_external_cdb_loader_without_native_terms(self) -> None:
        text = APP.read_text(encoding="utf-8")

        self.assertIn("def _load_external_cdb_case", text)
        self.assertIn("load_cdb", text)
        self.assertIn("chains_to_probe_points", text)
        self.assertIn("chains_to_segments", text)
        self.assertIn("chains_to_polygons", text)
        self.assertNotIn("rtdl_rayjoin", text)


if __name__ == "__main__":
    unittest.main()
