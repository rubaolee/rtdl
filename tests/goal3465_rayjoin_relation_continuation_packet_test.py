from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3465_rayjoin_relation_continuation_packet.py"
REPORT = ROOT / "docs" / "reports" / "goal3465_rayjoin_relation_continuation_packet_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3465_rayjoin_relation_continuation_packet_pod_2026-06-05.json"


class Goal3465RayJoinRelationContinuationPacketTest(unittest.TestCase):
    def test_packet_runner_chains_relation_continuations(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "rtdl.goal3465.rayjoin_relation_continuation_packet.v1",
            "grouped_count_by_id_compact_device_columns",
            "shape_pair_relation_bounds_overlap_area_cupy",
            "shape_pair_relation_witness_cupy",
            "all_grouped_sums_match_rows",
            "all_witnesses_resolved",
            "total_relation_plus_continuations_sec",
        ):
            self.assertIn(phrase, script)

    def test_report_records_packet_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3465",
            "current-performance packet",
            "Bounds-overlap area remains a proxy",
            "not clipped polygon output",
            "does not authorize",
            "Exact overlay-area continuation",
        ):
            self.assertIn(phrase, report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3465 pod artifact pending")
    def test_pod_artifact_records_stable_relation_packet(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3465.rayjoin_relation_continuation_packet.v1")
        self.assertEqual(payload["goal"], 3465)
        self.assertEqual(payload["iterations"], 4)
        self.assertTrue(payload["all_row_counts_stable"])
        self.assertTrue(payload["all_grouped_sums_match_rows"])
        self.assertTrue(payload["all_group_counts_stable"])
        self.assertTrue(payload["all_bounds_area_sums_stable"])
        self.assertTrue(payload["all_witnesses_resolved"])
        self.assertGreater(payload["row_counts"][0], 0)
        self.assertGreater(payload["grouped_left_row_counts"][0], 0)
        self.assertGreaterEqual(payload["total_relation_plus_continuations_sec"]["median"], 0.0)
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
