from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3230_rayjoin_public_count_claim_boundary_normalization_2026-06-03.md"
SUMMARY = ROOT / "docs" / "reports" / "goal3229_rayjoin_public_count_coverage_summary_2026-06-03.md"
OVERLAY = ROOT / "docs" / "reports" / "goal3225_rayjoin_public_overlay_active_count_probe_2026-06-03.json"
PIP = ROOT / "docs" / "reports" / "goal3227_rayjoin_public_pip_count_probe_2026-06-03.json"

CANONICAL_KEYS = {
    "public_speedup_claim_authorized",
    "rt_core_speedup_claim_authorized",
    "true_zero_copy_claim_authorized",
    "rayjoin_paper_reproduction_claim_authorized",
    "rtdl_beats_rayjoin_claim_authorized",
    "release_authorized",
}


class Goal3230RayJoinPublicCountClaimBoundaryNormalizationTest(unittest.TestCase):
    def _assert_canonical_false_boundary(self, boundary: dict[str, object]) -> None:
        self.assertEqual(set(boundary), CANONICAL_KEYS)
        self.assertTrue(all(value is False for value in boundary.values()))

    def test_overlay_artifact_uses_canonical_boundary_at_every_level(self) -> None:
        data = json.loads(OVERLAY.read_text(encoding="utf-8"))

        self.assertEqual(data["commit"], "92e16b8649f99aa62fbca0d0c97466a7a2f8eaa3")
        self._assert_canonical_false_boundary(data["claim_boundary"])
        for row in data["rows"]:
            self._assert_canonical_false_boundary(row["claim_boundary"])
            for measurement in row["measurements"]["prepared_overlay_active_count"]:
                self._assert_canonical_false_boundary(measurement["claim_boundary"])

    def test_pip_artifact_uses_canonical_boundary_at_every_level(self) -> None:
        data = json.loads(PIP.read_text(encoding="utf-8"))

        self.assertEqual(data["commit"], "92e16b8649f99aa62fbca0d0c97466a7a2f8eaa3")
        self._assert_canonical_false_boundary(data["claim_boundary"])
        for row in data["rows"]:
            self._assert_canonical_false_boundary(row["claim_boundary"])
            for measurement in row["measurements"]["prepared_pip_count"]:
                self._assert_canonical_false_boundary(measurement["claim_boundary"])

    def test_reports_describe_the_normalization_without_overclaiming(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        summary = SUMMARY.read_text(encoding="utf-8")

        for phrase in (
            "top, row, and measurement",
            "92e16b8649f99aa62fbca0d0c97466a7a2f8eaa3",
            "does not authorize release",
            "true zero-copy claims",
            "RayJoin paper-reproduction claims",
        ):
            self.assertIn(phrase, report)
        self.assertIn("normalize the six false claim-boundary flags", summary)


if __name__ == "__main__":
    unittest.main()
