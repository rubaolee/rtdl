from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1544_v1_5_4_optix_collect_k_launch_orchestration_negative_results_2026-05-08.md"


class Goal1544V154OptixCollectKLaunchOrchestrationNegativeResultsTest(unittest.TestCase):
    def test_report_records_rejected_paths_and_boundary(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("No new accepted performance improvement", text)
        self.assertIn("Raising the threshold forces broad merge levels", text)
        self.assertIn("do not replace the final parallel compact", text)
        self.assertIn("did not improve the largest target count", text)
        self.assertIn("deterministic device-side segmented prefix/compact", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
