from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2145_rayjoin_v2_spatial_join_first_slice_2026-05-16.md"
APP = ROOT / "examples" / "rtdl_rayjoin_v2_spatial_join_app.py"


class Goal2145RayjoinV2SpatialJoinFirstSliceReportTest(unittest.TestCase):
    def test_report_records_sources_scope_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        required = (
            "RayJoin: Fast and Precise Spatial Join",
            "https://gengl.me/publication/ics24/",
            "https://gengl.me/public/publications/ics24.pdf",
            "https://github.com/pwrliang/RayJoin",
            "point_to_polygon_positive_hit_rows",
            "segment_segment_intersection_rows",
            "overlay_pair_dependency_rows_with_lsi_pip_flags",
            "Full RayJoin paper reproduction",
            "OptiX/RT-core speedup evidence",
            "does not add app-specific native ABI names",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_app_uses_sparse_pip_not_full_matrix_policy(self) -> None:
        text = APP.read_text(encoding="utf-8")

        self.assertIn("rayjoin_point_location_positive_hits_reference", text)
        self.assertIn('result_mode="positive_hits"', text)
        self.assertIn('"pip": rayjoin_point_location_positive_hits_reference', text)
        self.assertNotIn("point_in_counties_reference", text)


if __name__ == "__main__":
    unittest.main()
