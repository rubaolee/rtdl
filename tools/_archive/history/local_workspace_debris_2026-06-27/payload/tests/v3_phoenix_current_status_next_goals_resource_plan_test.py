from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_PLAN = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_current_status_next_goals_resource_plan_2026-06-22.json"
)
MD_PLAN = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_current_status_next_goals_resource_plan_2026-06-22.md"
)


class V3PhoenixCurrentStatusNextGoalsResourcePlanTest(unittest.TestCase):
    def test_plan_blocks_release_and_all_app_until_focused_sources_exist(self) -> None:
        payload = json.loads(JSON_PLAN.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "phoenix_v3_redesign_in_progress_not_release")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["external_embedding_or_zero_copy_claim_authorized"])
        self.assertFalse(payload["all_app_pod_spend_authorized"])

        step1 = payload["completed"][1]
        self.assertEqual(step1["status"], "structural_credential_complete_performance_not_met")
        self.assertAlmostEqual(step1["runner_vs_legacy_geomean"], 0.9948584784435961)
        self.assertAlmostEqual(step1["legacy_vs_embree_geomean"], 2.942859650227)
        self.assertFalse(step1["material_set_a_candidate"])
        self.assertEqual(step1["external_review_verdict"], "approve_blocked_not_release")

        self.assertEqual(payload["next_goals"][0]["id"], "g1_rayjoin_legacy_materialization_audit")
        self.assertEqual(payload["next_goals"][0]["estimated_pod_hours_max"], 0.25)
        self.assertEqual(payload["next_goals"][1]["status"], "blocked_until_g1_finds_source")
        self.assertEqual(payload["next_goals"][4]["status"], "blocked")
        self.assertIn("goal_level_decision_audit", payload)

    def test_markdown_records_resource_estimate_and_non_authorization(self) -> None:
        markdown = MD_PLAN.read_text(encoding="utf-8")

        self.assertIn("Phoenix V3 Current Status", markdown)
        self.assertIn("RTDBSCAN runner vs legacy OptiX grouped-stream | `0.994858x`", markdown)
        self.assertIn("RTDBSCAN legacy vs Embree control | `2.942860x`", markdown)
        self.assertIn("RayJoin legacy materialization audit", markdown)
        self.assertIn("Running all-app now would mostly\nrepeat the old blended `1.012x` result", markdown)
        self.assertIn("This plan authorizes no release", markdown)
        self.assertIn("Release remains `redo_required`", markdown)


if __name__ == "__main__":
    unittest.main()
