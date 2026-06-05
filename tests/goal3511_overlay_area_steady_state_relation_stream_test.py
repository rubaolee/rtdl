from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"


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


if __name__ == "__main__":
    unittest.main()
