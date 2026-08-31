from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3154_rt_dbscan_current_head_a40_grouped_stream_refresh_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3154_pod_artifacts" / "rt_dbscan_current_head_a40_clean.json"


class Goal3154RTDBSCANCurrentHeadA40GroupedStreamRefreshTest(unittest.TestCase):
    def test_artifact_records_clean_current_head_pass(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["app"], "rt_dbscan")
        self.assertEqual(payload["source_commit"], "e38a90db634ad0b911f7857a3b2b8cea588cb529")
        self.assertEqual(payload["source_dirty"], [])
        self.assertEqual(payload["gpu"], "NVIDIA A40, 570.211.01")
        self.assertTrue(payload["signatures_match"])
        self.assertTrue(payload["grouped_stream_rt_core_accelerated"])
        self.assertTrue(payload["grouped_stream_avoids_neighbor_rows_and_full_adjacency_stream"])
        self.assertGreater(payload["min_grouped_stream_speedup_vs_prepared_cupy_grid"], 4.0)

    def test_all_rows_match_and_avoid_materialization(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["point_counts"], [32768, 65536, 131072])
        self.assertEqual(len(payload["rows"]), 3)
        for row in payload["rows"]:
            self.assertTrue(row["prepared_cupy_signature_match"])
            self.assertTrue(row["rt_count_signature_match"])
            self.assertTrue(row["grouped_stream_signature_match"])
            self.assertTrue(row["grouped_stream_rt_core_accelerated"])
            self.assertFalse(row["grouped_stream_materializes_neighbor_rows"])
            self.assertFalse(row["grouped_stream_materializes_directed_adjacency_stream"])
            self.assertGreater(row["grouped_stream_speedup_vs_prepared_cupy_grid"], 4.0)

    def test_claim_boundary_remains_blocked(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        boundary = dict(payload["claim_boundary"])

        self.assertTrue(boundary["canonical_live_harness"])
        for key, value in boundary.items():
            if key == "canonical_live_harness":
                continue
            self.assertFalse(value, key)

        report = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "not a new release gate",
            "not a new public claim",
            "public_speedup_claim_authorized: False",
            "paper_reproduction_claim_authorized: False",
            "broad_dbscan_speedup_claim_authorized: False",
            "native_engine_customization: False",
            "release_authorized: False",
        ):
            self.assertIn(phrase, report)

    def test_report_states_next_generic_front_door_target(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "v2.8-discoverable generic front-door contract",
            "fixed-radius graph/component continuation",
            "typed adjacency stream or grouped-stream producer metadata",
            "explicit user-selected partner continuation",
            "component-label output contract",
            "no `dbscan`, `cluster`, or `min_neighbors` vocabulary",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()

