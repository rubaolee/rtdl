from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT_MD = ROOT / "docs" / "reports" / "goal1507_v1_5_4_non_pod_optix_collect_k_local_readiness_2026-05-08.md"


class Goal1507V154NonPodOptixCollectKLocalReadinessTest(unittest.TestCase):
    def test_report_records_local_readiness_without_claim_expansion(self) -> None:
        text = REPORT_MD.read_text(encoding="utf-8")

        self.assertIn("No public performance claim", text)
        self.assertIn("accepted_goal1506_evidence=false", text)
        self.assertIn("local_fallback_smoke_only=true", text)
        self.assertIn("dynamic_row_width_single_thread_fallback", text)
        self.assertIn("row_width2_bounded_multi_tile_sort_merge", text)
        self.assertIn("does not authorize public speedup wording", text)

    def test_report_records_exact_next_pod_command(self) -> None:
        text = REPORT_MD.read_text(encoding="utf-8")

        self.assertIn(
            "OPTIX_PREFIX=/root/vendor/optix-sdk bash scripts/goal1506_v1_5_4_run_optix_collect_k_stage_profile_pod.sh",
            text,
        )


if __name__ == "__main__":
    unittest.main()
