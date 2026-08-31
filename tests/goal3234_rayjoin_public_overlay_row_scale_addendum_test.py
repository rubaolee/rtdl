from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3234_rayjoin_public_overlay_row_scale_addendum_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3234_rayjoin_public_overlay_row_scale_addendum_2026-06-03.json"
STDOUT = ROOT / "docs" / "reports" / "goal3234_rayjoin_public_overlay_row_scale_addendum_2026-06-03.stdout"

CANONICAL_KEYS = {
    "public_speedup_claim_authorized",
    "rt_core_speedup_claim_authorized",
    "true_zero_copy_claim_authorized",
    "rayjoin_paper_reproduction_claim_authorized",
    "rtdl_beats_rayjoin_claim_authorized",
    "release_authorized",
}


class Goal3234RayJoinPublicOverlayRowScaleAddendumTest(unittest.TestCase):
    def _assert_boundary(self, boundary: dict[str, object]) -> None:
        self.assertEqual(set(boundary), CANONICAL_KEYS)
        self.assertTrue(all(value is False for value in boundary.values()))

    def test_scale_artifact_records_large_public_overlay_rows(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3234)
        self.assertEqual(data["schema"], "rtdl.goal3234.rayjoin_public_overlay_row_scale_addendum.v1")
        self.assertEqual(data["commit"], "d19a8175d9e8c211aee2d1395dd5fa8b1ebb5223")
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["hardware"]["nvidia_smi"], "NVIDIA A40, 570.211.01")
        self.assertEqual(data["hardware"]["rtdl_optix_library"], "/root/rtdl_goal3151/build/librtdl_optix.so")

        rows = {row["case"]: row for row in data["rows"]}
        self.assertEqual(set(rows), {"overlay_county384_soil384", "overlay_county512_soil512"})
        expected = {
            "overlay_county384_soil384": (130320, 96),
            "overlay_county512_soil512": (233766, 121),
        }
        for case, (row_count, active_rows) in expected.items():
            with self.subTest(case=case):
                row = rows[case]
                measurement = row["measurements"]["prepared_optix_rows"][0]
                self.assertEqual(row["workload"], "overlay_seed")
                self.assertEqual(row["cpu_row_count"], row_count)
                self.assertEqual(row["cpu_active_overlay_rows"], active_rows)
                self.assertEqual(measurement["row_count"], row_count)
                self.assertEqual(measurement["symmetric_difference_count"], 0)
                self.assertTrue(measurement["row_set_matches_cpu"])
                self.assertIn("unattributed_prepared_total_minus_named_phases_sec", measurement)
                self.assertTrue(row["all_repeats_match_cpu_rows"])
                self.assertNotIn("active_seed_pairs", row["cpu_summary"])

    def test_scale_artifact_preserves_claim_boundaries(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self._assert_boundary(data["claim_boundary"])
        for row in data["rows"]:
            self._assert_boundary(row["claim_boundary"])
            for measurement in row["measurements"]["prepared_optix_rows"]:
                self._assert_boundary(measurement["claim_boundary"])

    def test_report_and_stdout_are_bounded(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        stdout = STDOUT.read_text(encoding="utf-8")

        for phrase in (
            "130320",
            "233766",
            "symmetric difference",
            "does not authorize release",
            "not to authorize a public speedup claim",
            "unattributed materialization/host overhead",
            "device-resident row-stream continuation remain future work",
        ):
            self.assertIn(phrase, report)
        self.assertIn("repeat overlay_county384_soil384/prepared_rows 1/1", stdout)
        self.assertIn("repeat overlay_county512_soil512/prepared_rows 1/1", stdout)
        self.assertIn("symdiff=0", stdout)


if __name__ == "__main__":
    unittest.main()
