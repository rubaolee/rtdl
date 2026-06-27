from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.v3_phoenix_barnes_hut_blocker_intake import (
    DEFAULT_JSON_OUT,
    DEFAULT_MD_OUT,
    build_payload,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_barnes_hut_blocker_intake.py"


class V3PhoenixBarnesHutBlockerIntakeTest(unittest.TestCase):
    def test_focused_fix_reclassifies_barnes_hut_blocker_without_release(self) -> None:
        payload = build_payload()

        self.assertEqual(payload["tool"], "v3_phoenix_barnes_hut_blocker_intake")
        self.assertEqual(payload["status"], "barnes_hut_focused_fix_intake_not_release")
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["full_all_app_rerun_authorized_by_this_packet"])

        projection = payload["projection"]
        self.assertAlmostEqual(projection["frozen_barnes_hut_app_geomean"], 0.8441965065233041)
        self.assertAlmostEqual(projection["projected_barnes_hut_app_geomean"], 1.008971208978369)
        self.assertGreaterEqual(projection["projected_barnes_hut_app_geomean"], 0.95)
        self.assertEqual(len(payload["replacement_rows"]), 6)

        runner = payload["runner_parity"]
        self.assertTrue(runner["runner_parity_with_existing_fused_partner"])
        self.assertAlmostEqual(runner["runner_vs_existing_fused_control_geomean"], 0.999328063165968)
        self.assertFalse(runner["historical_optix_reference_is_primary_claim"])

    def test_cli_writes_json_and_markdown(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--pretty"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(DEFAULT_JSON_OUT.exists())
        self.assertTrue(DEFAULT_MD_OUT.exists())
        markdown = DEFAULT_MD_OUT.read_text(encoding="utf-8")
        self.assertIn("Phoenix V3 Barnes-Hut Blocker Intake M7", markdown)
        self.assertIn("release_authorized: false", markdown)
        self.assertIn("Projected Barnes-Hut app geomean", markdown)
        self.assertIn("do_not_spend_more_barnes_hut_pod_time", markdown)


if __name__ == "__main__":
    unittest.main()
