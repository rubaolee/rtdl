from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "rtdl_hausdorff_distance_app.py"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3143_pod_artifacts"
    / "hausdorff_partner_exact_numba_pod_probe_2026-06-03.json"
)
REPORT = ROOT / "docs" / "reports" / "goal3150_hausdorff_release_boundary_key_normalization_2026-06-03.md"
FUTURE_TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


class Goal3150HausdorffReleaseBoundaryKeyNormalizationTest(unittest.TestCase):
    def test_app_legacy_numba_paths_carry_v2_8_false_boundary(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertGreaterEqual(source.count('"v2_6_release_authorized": False'), 2)
        self.assertGreaterEqual(source.count('"v2_8_release_authorized": False'), 3)
        self.assertIn("partner_numba_block_nearest_exact", source)

    def test_goal3143_artifact_rows_all_carry_v2_8_false_boundary(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertTrue(artifact["all_match"])
        for row in artifact["rows"]:
            with self.subTest(mode=row["mode"], copies=row["copies"]):
                self.assertIn("v2_8_release_authorized", row["claim_boundary"])
                self.assertFalse(row["claim_boundary"]["v2_8_release_authorized"])
                self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])
                self.assertFalse(row["claim_boundary"]["rt_core_speedup_claim_authorized"])
                self.assertFalse(row["claim_boundary"]["true_zero_copy_claim_authorized"])

    def test_report_and_future_note_document_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        future = FUTURE_TODO.read_text(encoding="utf-8")

        for phrase in (
            "no claim leak",
            "key-only artifact normalization",
            "Connection refused",
            "no pod rerun is required",
        ):
            self.assertIn(phrase, report)
        self.assertIn("directed_max_of_nearest_distance_2d", future)
        self.assertIn("hausdorff", future.lower())


if __name__ == "__main__":
    unittest.main()
