import unittest
from pathlib import Path

from scripts import goal1508_v1_5_4_optix_collect_k_tiled_preflight as preflight


ROOT = Path(__file__).resolve().parents[1]
API_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal1629_v1_6_x_optix_collect_k_large_count_guardrail_2026-05-09.md"


class Goal1629OptixCollectKLargeCountGuardrailTest(unittest.TestCase):
    def test_source_keeps_current_tiled_path_bounded_to_131072_candidates(self) -> None:
        text = API_CPP.read_text(encoding="utf-8")

        self.assertIn("kCollectKRowWidth2BaseMaxTiledCandidates = 131072", text)
        self.assertIn("kCollectKRowWidth2BaseMaxTileSegments = 64", text)
        self.assertIn("kCollectKRowWidth2BaseMaxPrefixBlocks = 512", text)
        self.assertIn("RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC", text)

    def test_preflight_rejects_counts_above_current_tiled_profile_boundary(self) -> None:
        case = preflight._case_for_count(
            131073,
            preflight.ROW_WIDTH2_TILE_SHARED_BYTES,
        )

        self.assertEqual(case["expected_native_path"], "dynamic_row_width_single_thread_fallback")
        self.assertEqual(case["predicted_profile_native_path"], "dynamic_row_width_single_thread_fallback")
        self.assertFalse(case["accepted_goal1506_profile_candidate"])

    def test_report_records_guardrail_without_claim_expansion(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("large_count_guardrail_recorded", text)
        self.assertIn("candidate_count <= 131072", text)
        self.assertIn("64 tiles", text)
        self.assertIn("not with a defer-merge-sync\n  regression", text)
        self.assertIn("does\nnot authorize public speedup wording", text)
        self.assertIn("stable\n`COLLECT_K_BOUNDED` promotion", text)
        self.assertIn("release action", text)


if __name__ == "__main__":
    unittest.main()
