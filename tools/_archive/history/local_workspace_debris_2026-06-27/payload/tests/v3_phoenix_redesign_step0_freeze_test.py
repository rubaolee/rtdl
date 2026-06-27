from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STEP0_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_redesign_step0_freeze_2026-06-22.json"
STEP0_MD = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_redesign_step0_freeze_2026-06-22.md"
RUNNER = ROOT / "scripts" / "phoenix_v3_serious_paired_v2x_runner.sh"


class V3PhoenixRedesignStep0FreezeTest(unittest.TestCase):
    def test_step0_freeze_records_non_release_controls(self) -> None:
        payload = json.loads(STEP0_JSON.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "step0_frozen_not_release")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertEqual(payload["cache_thread_status"], "closed_as_hygiene_only")
        self.assertEqual(payload["set_a_set_b_status"], "frozen_before_next_full_paired_run")
        self.assertEqual(payload["all_app_paired_runs_status"], "paused_until_runtime_trunk_executes")
        self.assertEqual(payload["runtime_trunk_status"], "not_yet_executing")
        self.assertTrue(all(payload["step0_exit_criteria"].values()))
        self.assertIn("goal_level_decision_audit", payload)

    def test_markdown_and_runner_guard_block_accidental_all_app_run(self) -> None:
        markdown = STEP0_MD.read_text(encoding="utf-8")
        self.assertIn("all_app_paired_runs_status: paused_until_runtime_trunk_executes", markdown)
        self.assertIn("PHOENIX_V3_RUNTIME_TRUNK_EXECUTED=1", markdown)

        runner = RUNNER.read_text(encoding="utf-8")
        self.assertIn("PHOENIX_V3_ALLOW_ALL_APP_RUN", runner)
        self.assertIn("PHOENIX_V3_RUNTIME_TRUNK_EXECUTED", runner)
        self.assertIn("exit 64", runner)


if __name__ == "__main__":
    unittest.main()
