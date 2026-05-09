import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1631_v1_6_x_optix_extended_defer_collect_k_test_sweep_2026-05-09.md"
TRANSCRIPT = ROOT / "docs" / "reports" / "goal1631_v1_6_x_optix_extended_defer_collect_k_test_sweep_2026-05-09.txt"


class Goal1631OptixExtendedDeferCollectKTestSweepTest(unittest.TestCase):
    def test_transcript_records_green_collect_k_sweep_with_both_diagnostics(self) -> None:
        text = TRANSCRIPT.read_text(encoding="utf-8")

        self.assertIn("git_commit 5adc806790ab09e9554e3f66c85cbf51a492db2e", text)
        self.assertIn("NVIDIA RTX A4500, 550.127.05, 20470 MiB", text)
        self.assertIn("RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC=1", text)
        self.assertIn("RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC=1", text)
        self.assertIn("collect_k_test_module_count 108", text)
        self.assertIn("Ran 420 tests", text)
        self.assertIn("\nOK\n", text)

    def test_report_keeps_internal_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("focused_collect_k_extended_defer_sweep_green", text)
        self.assertIn("`Ran 420 tests in", text)
        self.assertIn("`OK` present: `True`", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("stable `COLLECT_K_BOUNDED` promotion", text)
        self.assertIn("release action", text)


if __name__ == "__main__":
    unittest.main()
