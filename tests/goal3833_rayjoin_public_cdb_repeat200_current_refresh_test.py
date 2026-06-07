from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3833_rayjoin_public_cdb_repeat200_current_a5000" / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3833_rayjoin_public_cdb_repeat200_current_refresh_2026-06-07.md"


class Goal3833RayjoinPublicCdbRepeat200CurrentRefreshTest(unittest.TestCase):
    def test_artifact_records_current_head_public_cdb_route_results(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        rows = {row["case_id"]: row for row in payload["rows"]}

        self.assertTrue(payload["summary"]["all_counts_match"])
        self.assertEqual(payload["summary"]["row_count"], 3)
        self.assertTrue(payload["git_commit"].startswith("5cdb1cb5"))

        pip = rows["pip_county512"]
        self.assertTrue(pip["counts_match"])
        self.assertLess(pip["rtdl_optix_speedup_vs_cupy_cuda_core"], 1.0)
        self.assertIn("CuPy faster", pip["interpretation"])

        lsi = rows["lsi_county512_soil512"]
        self.assertTrue(lsi["counts_match"])
        self.assertGreater(lsi["rtdl_optix_speedup_vs_cupy_cuda_core"], 200.0)

        overlay = rows["overlay_county512_soil512"]
        self.assertTrue(overlay["counts_match"])
        self.assertGreater(overlay["rtdl_optix_speedup_vs_cupy_cuda_core"], 200.0)

    def test_report_records_mixed_route_guidance_without_claim_authorization(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3833",
            "not a RayJoin paper reproduction",
            "PIP count remains CuPy-favorable",
            "LSI count remains strongly RTDL/OptiX-favorable",
            "Overlay active-pair dependency count remains strongly RTDL/OptiX-favorable",
            "keep route choice visible to the user",
            "does not authorize release action",
            "automatic partner selection",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
