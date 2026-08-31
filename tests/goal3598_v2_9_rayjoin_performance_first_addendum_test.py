from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3598_v2_9_rayjoin_performance_first_addendum_2026-06-06.md"
GOAL3595 = ROOT / "docs" / "reports" / "goal3595_rayjoin_public_cdb_repeat200_a5000" / "summary.json"


class Goal3598V29RayJoinPerformanceFirstAddendumTest(unittest.TestCase):
    def test_addendum_tracks_goal3595_public_cdb_numbers(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        payload = json.loads(GOAL3595.read_text(encoding="utf-8"))
        self.assertEqual(payload["git_status_short"], "")
        self.assertTrue(payload["summary"]["all_counts_match"])
        for row in payload["rows"]:
            self.assertIn(row["case_id"], text)
        for phrase in (
            "CuPy `0.000437917s`",
            "RTDL/OptiX `0.000185231s`",
            "`113.693x`",
            "`91.742x`",
            "`12.8536x`",
        ):
            self.assertIn(phrase, text)

    def test_addendum_positions_rayjoin_without_overclaiming(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "not a single RayJoin app headline",
            "contract-level evidence",
            "use RTDL/OptiX where generic RT traversal pays",
            "use CuPy where dense CUDA-core logic is the best simple continuation",
            "generic exact point-in-closed-shape scalar count primitive",
            "Goal3599 closes the old silent-partial diagnosis",
            "Goal3601 closes the old same-contract repeat ambiguity",
            "clean near-parity same-contract row",
            "does not authorize",
            "automatic partner/backend selection",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
