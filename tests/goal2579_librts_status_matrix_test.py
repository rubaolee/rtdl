from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2579_librts_reproduction_status_and_next_targets_2026-05-24.md"


class LibRTSStatusMatrixTest(unittest.TestCase):
    def test_status_matrix_keeps_headline_claims_blocked(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("does not reproduce the paper's headline speedups", text)
        self.assertIn("AABB_INDEX_QUERY_2D", text)
        self.assertIn("no `LibRTS` native symbol", text)
        self.assertIn("We cannot say", text)
        self.assertIn("RTDL reproduces the LibRTS PPoPP 2025 headline speedups", text)


if __name__ == "__main__":
    unittest.main()
