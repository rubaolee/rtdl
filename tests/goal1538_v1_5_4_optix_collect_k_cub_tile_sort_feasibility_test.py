from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1538_v1_5_4_optix_collect_k_cub_tile_sort_feasibility_2026-05-08.md"


class Goal1538V154OptixCollectKCubTileSortFeasibilityTest(unittest.TestCase):
    def test_report_records_positive_cub_smoke(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("CUB block-level sorting is feasible", text)
        self.assertIn("cub::BlockMergeSort<Row2, 256, 8>", text)
        self.assertIn("cub_block_merge_sort_smoke_ok n=2048", text)
        self.assertIn("CUDA Driver API", text)

    def test_report_keeps_claim_boundary(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("feasibility only", text)
        self.assertIn("does not authorize speedup claims", text)
        self.assertIn("does not replace the accepted Goal 1536 late-level compact path", text)

    def test_next_direction_is_fail_closed(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("env-gated", text)
        self.assertIn("fail closed", text)
        self.assertIn("Keep the current accepted per-tile bitonic sort as the default", text)


if __name__ == "__main__":
    unittest.main()
