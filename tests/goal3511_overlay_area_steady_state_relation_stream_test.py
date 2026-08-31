from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3511_overlay_area_steady_state_relation_stream_pod_2026-06-05.json"


class Goal3511OverlayAreaSteadyStateRelationStreamTest(unittest.TestCase):
    def test_runner_exposes_steady_state_relation_stream_evidence(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "--relation-column-warmup-repeats",
            "--relation-stream-steady-state-evidence",
            "active_relation_device_columns",
            "active_relation_device_columns_warmup_secs",
            "active_relation_device_columns_best_warmup",
            "relation_column_warmup_repeats",
            "relation_stream_steady_state_evidence",
            "rtdl.goal3511.overlay_area_steady_state_relation_stream.v1",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_steady_state_goal_label_overrides_cache_label_when_requested(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("goal = 3511 if args.relation_stream_steady_state_evidence", text)
        self.assertIn("if args.relation_stream_steady_state_evidence", text)
        self.assertIn("if args.payload_cache_evidence", text)

    def test_pod_artifact_separates_steady_state_relation_columns_from_setup(self) -> None:
        data = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3511.overlay_area_steady_state_relation_stream.v1")
        self.assertEqual(data["goal"], 3511)
        self.assertTrue(data["rtdl_commit"].startswith("b156242b"))
        self.assertTrue(data["relation_stream_steady_state_evidence"])
        self.assertEqual(data["relation_column_warmup_repeats"], 3)
        self.assertEqual(data["payload_cache_mode"], "read")
        self.assertEqual(data["payload_cache_format"], "binary")
        self.assertTrue(data["payload_cache_metadata"]["read_used"])
        self.assertFalse(data["payload_cache_metadata"]["write_used"])

        warmups = data["timing_sec"]["active_relation_device_columns_warmup_secs"]
        self.assertEqual(len(warmups), 3)
        self.assertGreater(warmups[0], 0.1)
        self.assertLess(min(warmups[1:]), 0.01)
        self.assertLess(data["timing_sec"]["active_relation_device_columns"], 0.005)
        self.assertGreater(data["timing_sec"]["relation_discovery"], 1.0)

        self.assertEqual(data["relation_row_count"], 4543)
        self.assertEqual(data["candidate_relation_row_count"], 2274)
        self.assertEqual(data["supported_relation_row_count"], 2149)
        self.assertEqual(data["exact_positive_row_count"], data["observed_positive_row_count"])
        self.assertEqual(data["planned_triangle_pair_count"], 4070240)
        self.assertLess(data["total_area_abs_error"], 1.0e-8)
        self.assertLess(data["max_relation_abs_error"], 2.0e-9)

        for field, value in data["claim_boundary"].items():
            with self.subTest(field=field):
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
