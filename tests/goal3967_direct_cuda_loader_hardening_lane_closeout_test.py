import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3967_direct_cuda_loader_hardening_lane_closeout_2026-06-08.md"


class Goal3967DirectCudaLoaderHardeningLaneCloseoutTest(unittest.TestCase):
    def test_closeout_report_records_full_lane_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        required_fragments = [
            "Goal3951",
            "Goal3952",
            "Goal3954",
            "Goal3958",
            "Goal3962",
            "Goal3966",
            "19",
            "0 direct PTX loads; 28/28 direct loads use CUBIN",
            "OptiX pipeline PTX is intentionally still present",
            "does not authorize release",
            "does not authorize release,\npublic-speedup wording",
        ]
        for fragment in required_fragments:
            self.assertIn(fragment, text)

    def test_external_review_pairs_are_present_and_accepting(self) -> None:
        review_names = [
            "goal3956_claude_review_goal3951_3955_direct_cuda_cubin_debt_chain_2026-06-08.md",
            "goal3957_gemini_review_goal3951_3955_direct_cuda_cubin_debt_chain_2026-06-08.md",
            "goal3960_claude_review_goal3958_3959_point_group_nearest_cubin_2026-06-08.md",
            "goal3961_gemini_review_goal3958_3959_point_group_nearest_cubin_2026-06-08.md",
            "goal3964_claude_review_goal3962_3963_collect_k_cubin_zero_direct_ptx_2026-06-08.md",
            "goal3965_gemini_review_goal3962_3963_collect_k_cubin_zero_direct_ptx_2026-06-08.md",
        ]
        for name in review_names:
            review = ROOT / "docs" / "reviews" / name
            self.assertTrue(review.exists(), name)
            text = review.read_text(encoding="utf-8")
            self.assertIn("accept", text.lower(), name)
            self.assertNotIn("reject", text.lower(), name)

    def test_final_clean_packet_remains_claim_boundary_clean(self) -> None:
        packet = (
            ROOT
            / "docs"
            / "reports"
            / "goal3963_current_scale_clean_after_collect_k_cubin_hardening_2026-06-08"
            / "goal3963_current_scale_clean_after_collect_k_cubin.json"
        )
        data = json.loads(packet.read_text(encoding="utf-8"))
        self.assertTrue(data["all_pass"])
        self.assertEqual(10, data["json_pass_count"])
        for key in [
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
        ]:
            self.assertFalse(data[key], key)


if __name__ == "__main__":
    unittest.main()
