from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3174_v2_8_runtime_gap_bounded_collect_refresh_2026-06-03.md"


class Goal3174V28RuntimeGapBoundedCollectRefreshTest(unittest.TestCase):
    def test_robot_and_contact_rows_record_direct_bounded_collect_front_door(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}

        robot = rows["robot_collision"]
        self.assertIn("direct v2.8 bounded-collect typed-stream front door", robot["current_best_path"])
        self.assertIn("bounded-collect continuation now has a direct caller-column front door", robot["current_bottleneck"])
        self.assertIn("native typed flag/witness producer", robot["current_bottleneck"])
        self.assertIn("same-scale optional witness benchmarks", robot["current_bottleneck"])
        self.assertIn("Goal3173", robot["evidence_refs"])

        contact = rows["contact_manifold"]
        self.assertIn("direct v2.8 bounded-collect typed-stream front door", contact["current_best_path"])
        self.assertIn("bounded-collect continuation now has a direct caller-column front door", contact["current_bottleneck"])
        self.assertIn("native typed bounded-witness producer", contact["current_bottleneck"])
        self.assertIn("same-scale partner/native benchmarks", contact["current_bottleneck"])
        self.assertIn("Goal3173", contact["evidence_refs"])

        for row in (robot, contact):
            self.assertIn("torch/triton bounded collect", row["partner_position"])
            self.assertFalse(row["release_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertFalse(row["rt_core_speedup_claim_authorized"])
            self.assertFalse(row["true_zero_copy_claim_authorized"])

    def test_gap_map_still_validates_after_bounded_collect_refresh(self) -> None:
        validation = rt.validate_v2_8_benchmark_runtime_gap_map()

        self.assertEqual(validation["status"], "accept", validation)
        self.assertFalse(validation["release_authorized"])
        self.assertFalse(validation["public_speedup_claim_authorized"])
        self.assertFalse(validation["rt_core_speedup_claim_authorized"])
        self.assertFalse(validation["true_zero_copy_claim_authorized"])

    def test_report_records_refresh_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3173",
            "Robot collision",
            "Contact manifold",
            "direct bounded-collect typed-stream front door",
            "native typed flag/witness producer",
            "native typed bounded-witness producer",
            "`release_authorized: False`",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
