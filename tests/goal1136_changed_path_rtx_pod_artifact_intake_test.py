from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.goal1136_changed_path_rtx_pod_artifact_intake import build_intake


class Goal1136ChangedPathRtxPodArtifactIntakeTest(unittest.TestCase):
    def test_current_artifacts_are_valid_when_present(self) -> None:
        payload = build_intake()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["artifact_count"], 7)
        self.assertEqual(payload["valid_artifact_count"], 7)
        self.assertEqual(payload["missing_logs"], [])

    def test_db_row_materialization_is_checked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            logs = root / "logs"
            logs.mkdir()
            for name in (
                "database_analytics_compact_summary.log",
                "graph_visibility_edges_gate.log",
                "graph_visibility_edges_gate_rerun.log",
                "road_hazard_native_summary_count.log",
                "polygon_pair_overlap_phase_gate.log",
                "polygon_set_jaccard_phase_gate.log",
                "hausdorff_threshold_phase_gate.log",
            ):
                (logs / name).write_text("log\n", encoding="utf-8")
            fixtures = {
                "bootstrap_goal1135.json": {"status": "ok"},
                "graph_visibility_edges_gate.json": {"status": "pass", "strict_pass": True, "copies": 1},
                "road_hazard_native_summary_count.json": {"status": "pass", "strict_pass": True, "copies": 1},
                "polygon_pair_overlap_phase_gate.json": {"status": "pass", "copies": 1},
                "polygon_set_jaccard_phase_gate.json": {"status": "pass", "copies": 1},
                "hausdorff_threshold_phase_gate.json": {
                    "schema_version": "goal887_prepared_decision_phase_contract_v1",
                    "parameters": {"copies": 1},
                    "scenario": {
                        "mode": "optix",
                        "result": {"matches_oracle": True},
                        "timings_sec": {"optix_query_sec": {"median_sec": 0.1}},
                    },
                },
                "database_analytics_compact_summary.json": {
                    "results": [
                        {
                            "status": "ok",
                            "output_mode": "compact_summary",
                            "reported_native_db_phase_totals_sec": {"counter_status": "exported"},
                            "reported_run_phase_totals_sec": {"row_materializing_operation_count": 1},
                            "prepared_session_warm_query_sec": {"median_sec": 0.1},
                        }
                    ]
                },
            }
            for name, data in fixtures.items():
                (root / name).write_text(json.dumps(data), encoding="utf-8")

            payload = build_intake(root)

        self.assertFalse(payload["valid"])
        db_row = next(row for row in payload["rows"] if row["artifact"] == "database_analytics_compact_summary.json")
        self.assertIn("db_row_materializing_operations_present", db_row["findings"])


if __name__ == "__main__":
    unittest.main()
