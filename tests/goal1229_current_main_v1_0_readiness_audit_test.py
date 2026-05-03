from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1229_current_main_v1_0_readiness_audit as goal1229


ROOT = Path(__file__).resolve().parents[1]


class Goal1229CurrentMainV10ReadinessAuditTest(unittest.TestCase):
    def test_current_main_v1_0_audit_is_valid(self) -> None:
        payload = goal1229.build_audit()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["expected"]["reviewed_public_wording_count"], 12)
        self.assertEqual(
            payload["public_wording_state"]["blocked"],
            ["graph_analytics", "polygon_pair_overlap_area_rows"],
        )
        self.assertEqual(
            payload["public_wording_state"]["not_reviewed"],
            ["database_analytics", "polygon_set_jaccard"],
        )
        self.assertEqual(
            payload["public_wording_state"]["not_nvidia_target"],
            ["apple_rt_demo", "hiprt_ray_triangle_hitcount"],
        )

    def test_public_docs_have_current_main_wording_not_stale_goal1208_state(self) -> None:
        payload = goal1229.build_audit()
        for row in payload["surface_rows"]:
            with self.subTest(path=row["path"]):
                self.assertFalse(row["stale_current_main_phrases"])
        self.assertTrue(payload["checks"]["current_main_positioning_ok"])
        self.assertTrue(payload["checks"]["status_page_ok"])

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1229.json"
            output_md = Path(tmpdir) / "goal1229.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1229_current_main_v1_0_readiness_audit.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.assertIn("Goal1229 Current-Main v1.0 Readiness Audit", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertTrue(payload["valid"])
            self.assertIn("reviewed public RTX sub-path wording rows: `12`", markdown)
            self.assertIn("does not move the v0.9.8 release tag", markdown)


if __name__ == "__main__":
    unittest.main()
