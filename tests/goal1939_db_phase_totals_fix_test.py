from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1939_db_phase_totals_fix_2026-05-13.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal1939_db_phase_totals_fix_pod"
    / "control_database_analytics_100000_fixed_totals.json"
)


class Goal1939DbPhaseTotalsFixTest(unittest.TestCase):
    def test_artifact_has_nonzero_native_phase_totals(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        result = payload["results"][0]
        totals = result["reported_native_db_phase_totals_sec"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["output_mode"], "compact_summary")
        self.assertGreaterEqual(result["prepared_session_warm_query_sec"]["median_sec"], 1.0)
        self.assertEqual(totals["counter_status"], "exported")
        self.assertEqual(totals["operation_count"], 6)
        self.assertGreater(totals["traversal_sec"], 1.0)
        self.assertGreater(totals["exact_filter_sec"], 0.1)
        self.assertGreater(totals["output_pack_sec"], 0.03)
        self.assertGreater(totals["raw_candidate_count"], 0)
        self.assertGreater(totals["emitted_count"], 0)

    def test_report_preserves_control_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: db-phase-total-aggregation-fixed-release-still-blocked", text)
        self.assertIn("recursively descends", text)
        self.assertIn("not a v2 partner", text)
        self.assertIn("does not authorize v2.0", text)


if __name__ == "__main__":
    unittest.main()
