from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.v3_phoenix_set_ab_scorecard_gate import build_payload


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_set_ab_scorecard_gate.py"
JSON_OUT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json"
MD_OUT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md"


class V3PhoenixSetABScorecardGateTest(unittest.TestCase):
    def test_default_scorecard_classifies_current_serious_rows_and_blocks_release(self) -> None:
        payload = build_payload()

        self.assertEqual(payload["tool"], "v3_phoenix_set_ab_scorecard_gate")
        self.assertEqual(payload["status"], "classification_frozen_current_scorecard_not_release")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["all_app_pod_spend_authorized"])
        self.assertFalse(payload["release_candidate_under_two_number_bar"])
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))

        scorecard = payload["scorecard"]
        self.assertEqual(scorecard["row_count"], 52)
        self.assertEqual(scorecard["classified_row_count"], 52)
        self.assertEqual(scorecard["unclassified_row_count"], 0)
        self.assertEqual(scorecard["set_a_row_count"], 42)
        self.assertEqual(scorecard["set_b_row_count"], 10)
        self.assertAlmostEqual(scorecard["set_a_geomean_v3_vs_v2"], 1.0129340100769488)
        self.assertAlmostEqual(scorecard["set_b_geomean_v3_vs_v2"], 1.0069425307714026)
        self.assertEqual(scorecard["set_a_apps_over_1_05x"], 1)
        self.assertEqual(scorecard["set_a_required_apps_over_1_05x"], 5)
        self.assertEqual(scorecard["set_a_severe_regression_floor"], 0.9)
        self.assertEqual(scorecard["set_a_severe_regression_apps"], {"barnes_hut": 0.8441965065233041})
        self.assertEqual(scorecard["set_b_rows_below_0_95x"], 1)
        self.assertEqual(scorecard["focused_productized_material_probe_count_claimed"], 3)
        self.assertEqual(scorecard["focused_productized_material_probe_count_verified"], 3)
        self.assertEqual(
            scorecard["required_focused_productized_material_probe_count_before_full_all_app_pod_run"],
            2,
        )
        self.assertEqual(scorecard["missing_focused_productized_material_probe_count"], 0)
        self.assertEqual(
            [probe["id"] for probe in scorecard["verified_focused_productized_material_probes"]],
            [
                "aabb_runner_m2_1",
                "hausdorff_threshold_runner_m5_after_m6_1",
                "triangle_m19_env_corrected_productized_runner",
            ],
        )
        self.assertEqual(payload["unapproved_case_rows"], [])
        self.assertTrue(payload["checks"]["all_current_case_ids_whitelisted"])
        self.assertTrue(payload["checks"]["focused_probe_count_verified_from_artifacts"])
        self.assertTrue(payload["checks"]["set_a_severe_regressions_identified"])
        self.assertTrue(payload["checks"]["set_a_severe_regressions_block_pod_spend"])
        self.assertTrue(payload["checks"]["set_b_regressions_block_pod_spend"])

    def test_cli_writes_json_and_markdown_outputs(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--pretty",
                "--json-out",
                str(JSON_OUT),
                "--markdown-out",
                str(MD_OUT),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(JSON_OUT.exists())
        self.assertTrue(MD_OUT.exists())
        saved = json.loads(JSON_OUT.read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], payload["status"])
        markdown = MD_OUT.read_text(encoding="utf-8")
        self.assertIn("Phoenix V3 Set A / Set B Scorecard Gate", markdown)
        self.assertIn("all_app_pod_spend_authorized: false", markdown)
        self.assertIn("Focused material productized probes | 3 / 2 required", markdown)
        self.assertIn("productized-probe precondition is closed at 3/2", markdown)
        self.assertIn("full all-app pod spend remains blocked", markdown)
        self.assertNotIn("only one focused material", markdown)


if __name__ == "__main__":
    unittest.main()
