from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3816_recent_v2_10_docs_regression_slice_2026-06-07.md"


class Goal3816RecentV210DocsRegressionSliceTest(unittest.TestCase):
    def test_report_records_clean_pod_result_and_scope(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3816",
            "root@69.30.85.203 -p 22057",
            "692f4a49",
            "Ran 75 tests",
            "OK",
            "A5000/NVIDIA control evidence, not AMD hardware evidence",
            "validation with the Goal3785 runner",
        ):
            self.assertIn(phrase, text)

    def test_report_does_not_authorize_blocked_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "does not authorize release",
            "public speedup",
            "broad RT-core",
            "package-install",
            "true-zero-copy",
            "paper reproduction",
            "automatic partner selection",
            "AMD performance",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
