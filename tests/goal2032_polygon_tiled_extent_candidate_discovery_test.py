from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "rtdl_control_apps_cupy_rawkernel.py"
REPORT = ROOT / "docs" / "reports" / "goal2032_polygon_tiled_extent_candidate_discovery_2026-05-14.md"
JSON_REPORT = ROOT / "docs" / "reports" / "goal2032_polygon_tiled_extent_candidate_discovery_2026-05-14.json"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2032_polygon_tiled_extent_pod_936aff2f_dirty"


class Goal2032PolygonTiledExtentCandidateDiscoveryTest(unittest.TestCase):
    def test_source_uses_tiled_extent_candidate_helper(self) -> None:
        text = SOURCE.read_text(encoding="utf-8")

        self.assertIn("RTDL_CUPY_EXTENT_TILE_ROWS", text)
        self.assertIn("RTDL_CUPY_EXTENT_RIGHT_TILE_ROWS", text)
        self.assertIn("RTDL_CUPY_EXTENT_FREE_TILE_BLOCKS", text)
        self.assertIn("aabb_tiled_candidate_pair_payload_2d_partner_columns", text)
        self.assertNotIn("def _cupy_extent_candidate_indices", text)
        self.assertIn("tile_rows=_cupy_extent_tile_rows()", text)
        self.assertIn("right_tile_rows=_cupy_extent_right_tile_rows()", text)
        self.assertIn("free_tile_blocks=_cupy_extent_free_tile_blocks()", text)
        self.assertNotIn('left_columns["max_x"][:, None]', text)
        self.assertNotIn("left_max_x[:, None]", text)

    def test_report_records_goal2030_problem_and_goal2032_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("dense all-pairs CuPy extent mask", text)
        self.assertIn("failed at 16k copies", text)
        self.assertIn("16,384", text)
        self.assertIn("32,768", text)
        self.assertIn("65,536", text)
        self.assertIn("131,072", text)
        self.assertIn("not v2.0 release authorization", text)
        self.assertIn("not absolutely fair", text)

    def test_json_summary_pins_pod_results_and_blocks_claims(self) -> None:
        payload = json.loads(JSON_REPORT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "development-evidence-not-release-authorization")
        self.assertFalse(payload["claim_boundary"]["release_authorized"])
        self.assertFalse(payload["claim_boundary"]["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["source_commit_exact"])
        self.assertEqual(payload["key_results"]["goal2030_polygon_16000_dense_status"], "oom_dense_all_pairs_extent")
        self.assertEqual(payload["key_results"]["goal2032_polygon_16384_tiled_status"], "passed")
        self.assertLess(payload["key_results"]["polygon_pair_16384_ratio"], 0.30)
        self.assertLess(payload["key_results"]["polygon_pair_32768_ratio"], 0.45)
        self.assertLess(payload["key_results"]["polygon_pair_65536_ratio"], 0.55)
        self.assertLess(payload["key_results"]["polygon_pair_131072_ratio"], 0.80)
        self.assertLess(payload["key_results"]["polygon_jaccard_16384_ratio"], 0.25)
        self.assertLess(payload["key_results"]["polygon_jaccard_32768_ratio"], 0.30)
        self.assertLess(payload["key_results"]["polygon_jaccard_65536_ratio"], 0.45)
        self.assertLess(payload["key_results"]["polygon_jaccard_131072_ratio"], 0.70)

    def test_pod_artifacts_preserve_oracle_parity(self) -> None:
        for name in (
            "polygon_control_cupy_extent_tiled_16384.json",
            "polygon_control_cupy_extent_tiled_32768.json",
            "polygon_control_cupy_extent_tiled_65536.json",
            "polygon_control_cupy_extent_tiled_131072.json",
        ):
            path = ARTIFACT_DIR / name
            self.assertTrue(path.exists(), str(path))
            payload = json.loads(path.read_text(encoding="utf-8"))

            self.assertTrue(payload["all_match_v1_8_python_rtdl_oracle"])
            self.assertEqual(payload["source_commit_label"], "936aff2f_plus_goal2032_tiled_extent")
            rows = {row["app"]: row for row in payload["results"]}
            self.assertTrue(rows["polygon_pair_overlap_area_rows"]["matches_v1_8_python_rtdl_oracle"])
            self.assertTrue(rows["polygon_set_jaccard"]["matches_v1_8_python_rtdl_oracle"])


if __name__ == "__main__":
    unittest.main()
