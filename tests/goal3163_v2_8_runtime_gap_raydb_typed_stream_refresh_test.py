import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal3163_v2_8_runtime_gap_raydb_typed_stream_refresh_2026-06-03.md"
)


class Goal3163V28RuntimeGapRaydbTypedStreamRefreshTest(unittest.TestCase):
    def test_raydb_gap_row_records_typed_stream_front_door_and_remaining_boundary(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        raydb = rows["raydb_style"]

        self.assertIn("fused columnar grouped reductions", raydb["current_best_path"])
        self.assertIn("v2.8 grouped-reduction typed-stream front door", raydb["current_best_path"])
        self.assertIn("Numba is recommended only for unfused", raydb["partner_position"])
        self.assertIn("front-door schema for unfused grouped reductions now exists", raydb["current_bottleneck"])
        self.assertIn("native typed producer/residency evidence", raydb["current_bottleneck"])
        self.assertIn("Goal3162", raydb["evidence_refs"])
        self.assertFalse(raydb["automatic_partner_selection_allowed"])
        self.assertFalse(raydb["release_authorized"])
        self.assertFalse(raydb["true_zero_copy_claim_authorized"])

    def test_report_records_non_authorizing_status_refresh(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3162",
            "execute_grouped_reduction_typed_stream_partner_columns",
            "primitive-first fused grouped reductions",
            "native typed producer/residency evidence",
            "does not authorize release",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
