from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.v3_phoenix_remaining_blocker_queue import (
    DEFAULT_JSON_OUT,
    DEFAULT_MD_OUT,
    build_payload,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_remaining_blocker_queue.py"


class V3PhoenixRemainingBlockerQueueTest(unittest.TestCase):
    def test_queue_selects_spatial_lsi_without_authorizing_pod(self) -> None:
        payload = build_payload()

        self.assertEqual(payload["tool"], "v3_phoenix_remaining_blocker_queue")
        self.assertEqual(payload["status"], "m8_remaining_blocker_queue_not_release_not_pod")
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["full_all_app_pod_spend_authorized"])
        self.assertFalse(payload["focused_pod_spend_authorized"])

        projection = payload["score_projection_for_planning_only"]
        self.assertAlmostEqual(projection["planning_all_rows_geomean_after_covered_fixes"], 1.048703116681512)
        self.assertAlmostEqual(projection["planning_set_a_geomean_after_covered_fixes"], 1.03906646344581)
        self.assertEqual(projection["planning_set_a_app_wins_over_1_05x"], 1)
        self.assertEqual(projection["planning_set_a_app_wins_required"], 5)

        covered = payload["covered_pending_full_suite_validation"]
        self.assertEqual(len([row for row in covered if row["app_id"] == "barnes_hut"]), 6)
        self.assertTrue(
            any(
                row["row_id"].endswith("|embree|librts_embree_aabb_index")
                and row["planning_speedup"] > 1.9
                for row in covered
            )
        )

        active = payload["active_row_losses"]
        self.assertEqual(
            active[0]["row_id"],
            "goal2636_stress|spatial_rayjoin|rayjoin_lsi_authored_tiled_x2048|optix|rayjoin_optix_promoted_lsi_tiled_x2048",
        )
        self.assertTrue(active[0]["recommended_target"])
        self.assertEqual(payload["next_target_recommendation"]["id"], "spatial_rayjoin_lsi_optix_topology_stream")
        self.assertFalse(payload["next_target_recommendation"]["pod_authorized_now"])

        watch = payload["watch_rows"]
        self.assertEqual(watch[0]["case_id"], "librts_optix_aabb_index")
        self.assertLess(watch[0]["repeat9_focused_speedup"], 0.95)

    def test_cli_writes_outputs(self) -> None:
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
        self.assertIn("Phoenix V3 M8 Remaining Blocker Queue", markdown)
        self.assertIn("full_all_app_pod_spend_authorized: false", markdown)
        self.assertIn("spatial_rayjoin_lsi_optix_topology_stream", markdown)
        self.assertIn("pod authorized now: `false`", markdown)


if __name__ == "__main__":
    unittest.main()
