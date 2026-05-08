from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1533_v1_5_4_optix_collect_k_final_union_rank_negative_result_2026-05-08.md"
API_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
CORE_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal1533V154OptixCollectKFinalUnionRankNegativeResultTest(unittest.TestCase):
    def test_report_records_rejected_rank_only_path(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Rejected as an implementation path", text)
        self.assertIn("RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_MERGE", text)
        self.assertIn("failed output parity", text)
        self.assertIn("holes in the output rank space", text)
        self.assertIn("same_candidate_rows=False", text)

    def test_failed_prototype_is_not_left_in_source(self) -> None:
        source = API_CPP.read_text(encoding="utf-8") + CORE_CPP.read_text(encoding="utf-8")

        self.assertNotIn("RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_MERGE", source)
        self.assertNotIn("final_union_rank", source)

    def test_report_points_to_correct_next_design_requirement(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("duplicate-prefix information", text)
        self.assertIn("prefix/compact", text)
        self.assertIn("No source changes from this failed prototype were committed", text)


if __name__ == "__main__":
    unittest.main()
