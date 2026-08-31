from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3858_full_scale_after_triangle_route_2026-06-08.md"
ARTIFACT = ROOT / "docs/reports/goal3858_full_scale_after_triangle_route_a5000/summary.json"
TRIANGLE_STDOUT = (
    ROOT
    / "docs/reports/goal3858_full_scale_after_triangle_route_a5000/outputs/"
    / "triangle_counting_optix_rt_graph_2a1_scale_default_2048.stdout.json"
)


class Goal3858FullScaleAfterTriangleRouteTest(unittest.TestCase):
    def test_full_scale_packet_passes_all_rows(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertTrue(payload["all_pass"])
        self.assertEqual(payload["json_pass_count"], 10)
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_rt_core_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])

        rows = payload["rows"]
        self.assertEqual(len(rows), 10)
        self.assertTrue(all(row["status"] == "pass" for row in rows))
        self.assertTrue(all(row["stderr_bytes"] == 0 for row in rows))
        self.assertTrue(
            all(row["semantic_stdout_check"]["stdout_json_parseable"] for row in rows)
        )
        self.assertTrue(
            all(not row["semantic_stdout_check"]["claim_flag_violations"] for row in rows)
        )

    def test_triangle_row_uses_corrected_rt_graph_route(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        rows = {row["row_id"]: row for row in payload["rows"]}

        self.assertIn("triangle_counting_optix_rt_graph_2a1_scale_default_2048", rows)
        self.assertNotIn("triangle_counting_optix_scale_default_native_2048", rows)

        triangle = json.loads(TRIANGLE_STDOUT.read_text(encoding="utf-8"))
        self.assertEqual(triangle["mode"], "rt_graph_2a1_generic_rt")
        self.assertTrue(triangle["triangle_count_matches_oracle"])
        self.assertTrue(triangle["rt_core_accelerated"])
        self.assertEqual(
            triangle["rt_core_path"],
            "generic_prepared_triangle_scene_3d_any_hit_weighted_sum",
        )
        self.assertEqual(triangle["oracle_triangle_count"], 4096)
        self.assertEqual(triangle["generic_rt_weighted_triangle_count"], 4096)
        self.assertEqual(triangle["primitive_count"], 10240)
        self.assertEqual(triangle["ray_count"], 4096)
        self.assertEqual(triangle["rt_graph_fixture_copies"], 2048)
        self.assertLess(triangle["timing_ms"]["query_median_ms"], 0.5)
        self.assertFalse(triangle["generic_rt_summary"]["rows_materialized"])

    def test_report_records_full_refresh_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "All 10 calibrated default rows passed",
            "triangle_counting_optix_rt_graph_2a1_scale_default_2048",
            "0.176 ms",
            "not release authorization",
            "not public speedup wording",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
