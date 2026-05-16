from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2126_public_linux_gtx1070"


class PublicHausdorffLinuxSmokePerfArtifactsTest(unittest.TestCase):
    def test_artifacts_have_exact_parity_and_claim_boundaries(self) -> None:
        expected = (8192, 32768, 65536, 131072)
        for sample_count in expected:
            with self.subTest(sample_count=sample_count):
                path = ARTIFACT_DIR / f"public_hd_{sample_count}.json"
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["sample_count"], sample_count)
                boundary = payload["claim_boundary"]
                self.assertTrue(boundary["public_dataset_evidence"])
                self.assertTrue(boundary["xy_projection_only"])
                self.assertFalse(boundary["xhd_paper_exact_dataset_evidence"])
                self.assertFalse(boundary["three_dimensional_surface_hausdorff_claim"])
                self.assertFalse(boundary["release_speedup_claim_authorized"])
                self.assertIn("GTX 1070", payload["gpu"])
                self.assertEqual(len(payload["rows"]), 2)
                for row in payload["rows"]:
                    self.assertTrue(row["matches_cupy"])
                    self.assertLess(float(row["rtdl_vs_cupy_ratio"]), 4.0)

    def test_largest_public_smoke_rows_are_faster_than_cupy(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "public_hd_131072.json").read_text(encoding="utf-8"))
        ratios = {row["case"]: float(row["rtdl_vs_cupy_ratio"]) for row in payload["rows"]}
        self.assertLess(ratios["stanford_dragon_xy_shifted"], 0.5)
        self.assertLess(ratios["stanford_dragon_vs_happy_xy"], 0.35)


if __name__ == "__main__":
    unittest.main()
