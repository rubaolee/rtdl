import unittest
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
SCALING_PROBE = ROOT / "scripts" / "goal1503_v1_5_4_optix_collect_k_scaling_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal1650_v1_6_x_optix_collect_k_fastest_extended_capacity_2026-05-10.md"
POST_196608 = ROOT / "docs" / "reports" / "goal1650_post_fastest_196608.json"
POST_262144 = ROOT / "docs" / "reports" / "goal1650_post_fastest_262144.json"


class Goal1650OptixCollectKFastestExtendedCapacityTest(unittest.TestCase):
    def test_fastest_candidate_selects_extended_capacity(self) -> None:
        api = API.read_text(encoding="utf-8")

        self.assertIn(
            "collect_k_use_fastest_candidate() || collect_k_extended_128_tile_diagnostic()",
            api,
        )
        self.assertIn("kCollectKRowWidth2ExtendedMaxTiledCandidates", api)
        self.assertIn("kCollectKRowWidth2ExtendedMaxTileSegments", api)

    def test_expected_path_helper_matches_fastest_extended_capacity(self) -> None:
        text = SCALING_PROBE.read_text(encoding="utf-8")

        self.assertIn("RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE", text)
        self.assertIn("RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC", text)
        self.assertIn("else 131072", text)

    def test_report_records_scope_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`fastest_candidate_extended_capacity_enabled`", text)
        self.assertIn("candidate_count=262144", text)
        self.assertIn("total_ms=0.681118", text)
        self.assertIn("Python expected-path helper was also updated", text)
        self.assertIn("Post-Change A4500 Evidence", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("Post-Change A4500 Evidence", text)

    def test_post_change_artifacts_validate_fastest_without_extended_flag(self) -> None:
        case_196608 = json.loads(POST_196608.read_text(encoding="utf-8"))["cases"][0]
        case_262144 = json.loads(POST_262144.read_text(encoding="utf-8"))["cases"][0]

        self.assertEqual(case_196608["candidate_count"], 196608)
        self.assertEqual(case_262144["candidate_count"], 262144)
        self.assertEqual(case_196608["stage_profile"]["topology"]["native_path"], "row_width2_bounded_multi_tile_sort_merge")
        self.assertEqual(case_262144["stage_profile"]["topology"]["native_path"], "row_width2_bounded_multi_tile_sort_merge")
        self.assertTrue(case_196608["same_candidate_rows"])
        self.assertTrue(case_262144["same_candidate_rows"])
        self.assertLess(case_196608["stage_profile"]["stage_median_ms"]["total_ms"], 1.0)
        self.assertLess(case_262144["stage_profile"]["stage_median_ms"]["total_ms"], 1.0)


if __name__ == "__main__":
    unittest.main()
